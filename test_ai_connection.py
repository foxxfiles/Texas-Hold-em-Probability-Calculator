import json
import os
import time
import traceback
from openai import OpenAI
import requests
import logging
import sys

# Configuracion del logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_connection_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("api_test")

def test_ai_connections(verbose=True, timeout=30):
    """
    Prueba las conexiones a los modelos configurados en config.json
    
    Args:
        verbose (bool): Si es True, muestra informacion detallada
        timeout (int): Tiempo maximo de espera para las conexiones en segundos
    """
    
    logger.info("Iniciando pruebas de conexiones a modelos de IA...")
    start_time = time.time()
    
    # Verificar si existe el archivo de configuracion
    if not os.path.exists("config.json"):
        logger.error("No se encontro el archivo config.json")
        return False
    
    # Cargar configuracion
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            if verbose:
                # Mostrar configuración sin exponer claves API
                safe_config = {}
                for k, v in config.items():
                    if k != 'api':
                        safe_config[k] = v
                    else:
                        safe_config['api'] = {}
                        for api_name, api_conf in v.items():
                            safe_config['api'][api_name] = {
                                **api_conf,
                                'api_key': '***REDACTED***' if 'api_key' in api_conf and api_conf['api_key'] else 'Sin autenticación'
                            }
                logger.debug(f"Contenido del config (claves API ocultas): {json.dumps(safe_config, indent=2)}")
    except Exception as e:
        logger.error(f"Error al cargar el archivo config.json: {e}")
        logger.debug(traceback.format_exc())
        return False
    
    if "api" not in config:
        logger.error("No se encontro la seccion 'api' en config.json")
        return False
    
    # Probar cada modelo
    successful_models = []
    failed_models = []
    skipped_models = []
    results = {}
    
    # Detectar si hay modelos LMStudio
    lmstudio_models = [name for name, conf in config["api"].items() 
                       if conf.get("api_type", "").lower() == "openai" and not conf.get("api_key")]
    if lmstudio_models:
        logger.info(f"Detectados {len(lmstudio_models)} modelos sin autenticación (posiblemente LMStudio): {', '.join(lmstudio_models)}")
        logger.info("Estos modelos se probarán sin token de autenticación")
    
    # Primero listar todos los modelos que se van a probar
    logger.info(f"Se probaran {len(config['api'])} modelos: {', '.join(config['api'].keys())}")
    
    for model_name, model_config in config["api"].items():
        logger.info(f"\n{'='*30}\nProbando conexion a {model_name}...")
        
        # Verificar configuracion basica
        required_fields = ["api_type", "api_base_url", "model"]
        # No requerimos api_key para endpoints sin autenticación como LMStudio
        missing_fields = [field for field in required_fields if field not in model_config]
        
        if missing_fields:
            error_msg = f"Configuracion incompleta para {model_name}. Faltan campos: {', '.join(missing_fields)}"
            logger.error(error_msg)
            failed_models.append(model_name)
            results[model_name] = {"status": "error", "reason": error_msg}
            continue
        
        # Si api_enabled esta presente y es False, saltamos este modelo
        if not model_config.get("api_enabled", True):
            logger.info(f"Modelo {model_name} desactivado en config. Saltando prueba.")
            skipped_models.append(model_name)
            results[model_name] = {"status": "skipped", "reason": "API desactivada en configuracion"}
            continue
            
        try:
            test_start_time = time.time()
            
            if model_config["api_type"].lower() == "openai":
                test_openai_connection(model_name, model_config, verbose, timeout, 
                                      successful_models, failed_models, results)
                
            elif model_config["api_type"].lower() == "anthropic":
                test_anthropic_connection(model_name, model_config, verbose, timeout,
                                         successful_models, failed_models, results)
                
            else:
                error_msg = f"Tipo de API no soportado: {model_config['api_type']}"
                logger.error(error_msg)
                failed_models.append(model_name)
                results[model_name] = {"status": "error", "reason": error_msg}
                
            test_duration = time.time() - test_start_time
            if model_name in results:
                results[model_name]["duration"] = f"{test_duration:.2f}s"
                
        except Exception as e:
            error_msg = f"Error inesperado al conectar con {model_name}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            failed_models.append(model_name)
            results[model_name] = {
                "status": "error", 
                "reason": error_msg,
                "traceback": traceback.format_exc() if verbose else None
            }
    
    # Resumen
    total_duration = time.time() - start_time
    
    print("\n" + "="*70)
    logger.info(f"RESUMEN DE PRUEBAS DE CONEXION (duracion total: {total_duration:.2f}s):")
    logger.info(f"✅ Modelos conectados correctamente: {len(successful_models)}")
    if successful_models:
        for model in successful_models:
            model_info = f"{model} ({results[model]['duration']})"
            if "latency" in results[model]:
                model_info += f", latencia: {results[model]['latency']}"
            logger.info(f"   - {model_info}")
    
    logger.info(f"❌ Modelos con errores: {len(failed_models)}")
    if failed_models:
        for model in failed_models:
            logger.info(f"   - {model}: {results[model]['reason']}")
    
    logger.info(f"⏩ Modelos omitidos: {len(skipped_models)}")
    if skipped_models:
        for model in skipped_models:
            logger.info(f"   - {model}: {results[model]['reason']}")
    
    logger.info("="*70)
    
    # Guardar resultados en un archivo
    results_file = "connection_test_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_duration": f"{total_duration:.2f}s",
            "successful": len(successful_models),
            "failed": len(failed_models),
            "skipped": len(skipped_models),
            "results": results
        }, f, indent=2)
    
    logger.info(f"Resultados detallados guardados en {results_file}")
    
    return len(failed_models) == 0

def test_openai_connection(model_name, model_config, verbose, timeout, 
                         successful_models, failed_models, results):
    """Prueba la conexion a una API tipo OpenAI"""
    
    logger.info(f"Probando conexion a {model_name} (tipo: OpenAI)...")
    
    if verbose:
        logger.debug(f"Configuracion para {model_name}:")
        logger.debug(f"  - URL Base: {model_config['api_base_url']}")
        logger.debug(f"  - Modelo: {model_config['model']}")
        logger.debug(f"  - Autenticacion: {'No requerida' if not model_config.get('api_key') else 'Requerida'}")
        
    try:
        # Crear cliente OpenAI con timeout
        # Si api_key no está presente o está vacía, usamos None para endpoints sin autenticación (LMStudio)
        client_kwargs = {
            "base_url": model_config["api_base_url"],
            "timeout": timeout
        }
        
        # Solo agregamos api_key si existe y no está vacía
        if model_config.get("api_key"):
            client_kwargs["api_key"] = model_config["api_key"]
        else:
            # Para LMStudio y otros sin autenticación, necesitamos un valor que no genere un 'Bearer ' vacío
            client_kwargs["api_key"] = None
            
        client = OpenAI(**client_kwargs)
        
        # Guardar tiempo inicial para medir latencia
        request_start = time.time()
        
        # Test simple
        prompt = "Responde solo con un 'OK' para confirmar que estas funcionando."
        logger.debug(f"Enviando prompt de prueba: '{prompt}'")
        
        response = client.chat.completions.create(
            model=model_config["model"],
            messages=[
                {"role": "system", "content": "Eres un asistente que responde de forma muy corta."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        
        # Calcular latencia
        latency = time.time() - request_start
        
        if response.choices and response.choices[0].message:
            logger.info(f"✅ Conexion exitosa a {model_name} (latencia: {latency:.2f}s)")
            logger.info(f"Respuesta: {response.choices[0].message.content}")
            
            if verbose:
                logger.debug(f"Response ID: {response.id}")
                logger.debug(f"Model: {response.model}")
                
            successful_models.append(model_name)
            results[model_name] = {
                "status": "success",
                "latency": f"{latency:.2f}s",
                "response": response.choices[0].message.content,
                "model_details": {
                    "id": response.id,
                    "model": response.model
                } if verbose else None
            }
        else:
            error_msg = f"No se recibio respuesta valida de {model_name}"
            logger.error(f"❌ {error_msg}")
            failed_models.append(model_name)
            results[model_name] = {"status": "error", "reason": error_msg}
            
    except Exception as e:
        error_msg = f"Error al conectar con {model_name}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.debug(traceback.format_exc())
        failed_models.append(model_name)
        results[model_name] = {
            "status": "error", 
            "reason": error_msg,
            "traceback": traceback.format_exc() if verbose else None
        }

def test_anthropic_connection(model_name, model_config, verbose, timeout,
                            successful_models, failed_models, results):
    """Prueba la conexion a una API tipo Anthropic (Claude)"""
    
    logger.info(f"Probando conexion a {model_name} (tipo: Anthropic)...")
    
    if verbose:
        logger.debug(f"Configuracion para {model_name}:")
        logger.debug(f"  - URL Base: {model_config['api_base_url']}")
        logger.debug(f"  - Modelo: {model_config['model']}")
        logger.debug(f"  - Version API: {model_config.get('api_version', '2023-06-01')}")
        logger.debug(f"  - Autenticacion: {'No requerida' if not model_config.get('api_key') else 'Requerida'}")
        
    try:
        # Para Anthropic (Claude) usamos requests directamente
        headers = {
            "content-type": "application/json",
            "anthropic-version": model_config.get("api_version", "2023-06-01")
        }
        
        # Solo añadimos la clave de API si está presente (para endpoints que requieren autenticación)
        if model_config.get("api_key"):
            headers["x-api-key"] = model_config["api_key"]
        
        prompt = "Responde solo con un 'OK' para confirmar que estas funcionando."
        logger.debug(f"Enviando prompt de prueba: '{prompt}'")
        
        data = {
            "model": model_config["model"],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 10
        }
        
        # Guardar tiempo inicial para medir latencia
        request_start = time.time()
        
        response = requests.post(
            f"{model_config['api_base_url']}/messages",
            headers=headers,
            json=data,
            timeout=timeout
        )
        
        # Calcular latencia
        latency = time.time() - request_start
        
        if response.status_code == 200:
            response_json = response.json()
            content = response_json.get('content', [])
            text = content[0]['text'] if content and isinstance(content, list) else "No content"
            
            logger.info(f"✅ Conexion exitosa a {model_name} (latencia: {latency:.2f}s)")
            logger.info(f"Respuesta: {text}")
            
            if verbose:
                logger.debug(f"Response ID: {response_json.get('id', 'N/A')}")
                logger.debug(f"Response completo: {json.dumps(response_json, indent=2)}")
                
            successful_models.append(model_name)
            results[model_name] = {
                "status": "success",
                "latency": f"{latency:.2f}s",
                "response": text,
                "model_details": response_json if verbose else None
            }
        else:
            error_msg = f"Error HTTP {response.status_code}: {response.text}"
            logger.error(f"❌ Error en {model_name}: {error_msg}")
            
            if verbose:
                try:
                    error_json = response.json()
                    logger.debug(f"Detalles del error: {json.dumps(error_json, indent=2)}")
                except:
                    logger.debug(f"Respuesta de error (raw): {response.text}")
                    
            failed_models.append(model_name)
            results[model_name] = {
                "status": "error", 
                "reason": error_msg,
                "http_status": response.status_code,
                "error_details": response.text
            }
    
    except requests.exceptions.Timeout:
        error_msg = f"Timeout al conectar con {model_name} (limite: {timeout}s)"
        logger.error(f"❌ {error_msg}")
        failed_models.append(model_name)
        results[model_name] = {"status": "error", "reason": error_msg}
        
    except Exception as e:
        error_msg = f"Error al conectar con {model_name}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.debug(traceback.format_exc())
        failed_models.append(model_name)
        results[model_name] = {
            "status": "error", 
            "reason": error_msg,
            "traceback": traceback.format_exc() if verbose else None
        }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Prueba conexiones a APIs de IA')
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help='Mostrar informacion detallada de depuracion')
    parser.add_argument('--timeout', '-t', type=int, default=30,
                        help='Timeout para conexiones en segundos (default: 30)')
    
    args = parser.parse_args()
    
    result = test_ai_connections(verbose=args.verbose, timeout=args.timeout)
    sys.exit(0 if result else 1)  # Codigo de salida para CI/CD