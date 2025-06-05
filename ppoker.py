"""
Calculadora de Probabilidades de Texas Hold'em
----------------------------------------------
Esta aplicación calcula las probabilidades de ganar en una partida de poker
Texas Hold'em basándose en las cartas de tu mano, las cartas comunitarias
y el número de oponentes. También proporciona consejos estratégicos de
modelos de IA y permite chatear directamente con el asistente.

Autor: [Tu nombre aquí]
Versión: 1.1
"""

import tkinter as tk
from tkinter import ttk
import random
import math
import json
import os
import threading
import requests
from openai import OpenAI


class TexasHoldemCalculator:
    """
    Clase principal para la calculadora de probabilidades de Texas Hold'em.
    Proporciona una interfaz gráfica para seleccionar cartas, calcular probabilidades
    y obtener consejos de IA.
    """
    
    #----------------------------------------
    # Métodos de inicialización
    #----------------------------------------
    
    def __init__(self, root):
        """Inicializa la aplicación"""
        self.root = root
        self.root.title("Calculadora de Probabilidades de Texas Hold'em")
        self.root.geometry("1150x760")  # Ventana más ancha para la distribución en dos columnas
        self.root.configure(bg="#05422b")  # Verde oscuro como fondo principal
        
        # Variables de estado
        self.hand_cards = []  # Cartas de la mano del jugador
        self.table_cards = []  # Cartas de la mesa
        self.opponents = 1    # Número de oponentes
        self.card_buttons = {}  # Referencias a botones
        
        # Inicialización del mazo
        self.all_cards = []
        self.create_deck()
        
        # Configuración de estilos
        self.setup_styles()
        
        # Configuración de IA
        self.ai_models = {}
        self.ai_clients = {}
        self.load_ai_config()
        
        # Crear interfaz
        self.create_widgets()
    
    def setup_styles(self):
        """Configura los estilos para la interfaz"""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configuración de estilos
        self.style.configure("TFrame", background="#05422b")
        self.style.configure("TButton", background="#1a7b3e", foreground="white", 
                           borderwidth=0, font=("Arial", 10, "bold"))
        self.style.map("TButton", background=[("active", "#159947"), ("pressed", "#0d6e32")])
        self.style.configure("TLabel", background="#05422b", foreground="white", font=("Arial", 10))
        self.style.configure("Header.TLabel", background="#05422b", foreground="gold", 
                           font=("Arial", 16, "bold"))
        self.style.configure("Subheader.TLabel", background="#05422b", foreground="gold", 
                           font=("Arial", 12, "bold"))
        self.style.configure("Result.TLabel", background="#05422b", foreground="#ffd700", 
                           font=("Arial", 12, "bold"))
    
    def create_deck(self):
        """Crea el mazo completo de cartas"""
        suits = ["c", "d", "h", "s"]  # clubs, diamonds, hearts, spades
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        
        # Crear todas las combinaciones de cartas
        for suit in suits:
            for rank in ranks:
                self.all_cards.append(f"{rank}{suit}")
    
    def load_ai_config(self):
        """Carga la configuración de los modelos AI desde config.json"""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    if "api" in config:
                        self.ai_models = config["api"]
                        print(f"Modelos cargados: {list(self.ai_models.keys())}")
                        
                        # Inicializar clientes de API
                        for model_name, model_config in self.ai_models.items():
                            if model_config["api_type"] == "openai":
                                try:
                                    client = OpenAI(
                                        api_key=model_config["api_key"],
                                        base_url=model_config["api_base_url"]
                                    )
                                    self.ai_clients[model_name] = client
                                    print(f"Cliente inicializado para {model_name}")
                                except Exception as e:
                                    print(f"Error al inicializar cliente para {model_name}: {e}")
                            # Aquí se pueden agregar otros tipos de API
            else:
                print("No se encontró archivo config.json")
        except Exception as e:
            print(f"Error al cargar configuración AI: {e}")
            self.ai_models = {}
    
    #----------------------------------------
    # Creación de la interfaz
    #----------------------------------------
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz gráfica"""
        # Frame principal - layout vertical
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="CALCULADORA DE TEXAS HOLD'EM", style="Header.TLabel")
        title_label.pack(pady=(0, 10))
        
        # Panel superior con dos columnas para aprovechar mejor el espacio
        top_panel = ttk.Frame(main_frame)
        top_panel.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Panel izquierdo para cartas
        left_panel = ttk.Frame(top_panel)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Panel derecho para recomendaciones
        right_panel = ttk.Frame(top_panel)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Crear las secciones principales en el panel izquierdo
        self.create_cards_section(left_panel)
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        self.create_deck_section(left_panel)
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        self.create_controls_section(left_panel)
        
        # Crear las secciones de recomendación y consejos en el panel derecho
        self.create_recommendations_section(right_panel)
        self.create_ai_advice_section(right_panel)
    
    def create_cards_section(self, parent):
        """Crea la sección para mostrar las cartas seleccionadas"""
        top_panel = ttk.Frame(parent)
        top_panel.pack(fill=tk.X, pady=5)
        
        # Sección para cartas comunitarias
        community_section = ttk.Frame(top_panel)
        community_section.pack(pady=5)
        
        community_label = ttk.Label(community_section, text="CARTAS COMUNITARIAS", style="Subheader.TLabel")
        community_label.pack(pady=(0, 5))
        
        # Frame para las cartas comunitarias
        self.community_frame = ttk.Frame(community_section)
        self.community_frame.pack()
        
        # Mostrar slots vacíos para las cartas comunitarias
        for _ in range(5):
            self.display_empty_slot(self.community_frame, "community")
            
        # Sección para la mano del jugador
        hand_section = ttk.Frame(top_panel)
        hand_section.pack(pady=10)
        
        hand_label = ttk.Label(hand_section, text="TU MANO", style="Subheader.TLabel")
        hand_label.pack(pady=(0, 5))
        
        # Frame para las cartas del jugador
        self.hand_frame = ttk.Frame(hand_section)
        self.hand_frame.pack()
        
        # Mostrar slots vacíos para la mano
        for _ in range(2):
            self.display_empty_slot(self.hand_frame, "player")
    
    def create_deck_section(self, parent):
        """Crea la sección para seleccionar cartas del mazo"""
        selection_panel = ttk.Frame(parent)
        selection_panel.pack(fill=tk.X, pady=5)
        
        selection_label = ttk.Label(selection_panel, text="SELECCIONA TUS CARTAS", style="Subheader.TLabel")
        selection_label.pack(pady=(0, 5))
        
        # Instrucciones
        instruction_label = ttk.Label(selection_panel, 
                                     text="Haz clic en las cartas para seleccionarlas (2 para tu mano, 5 para la mesa)",
                                     foreground="#ffd700", background="#05422b", font=("Arial", 9))
        instruction_label.pack(pady=(0, 5))
        
        # Frame para el mini-deck
        self.card_selection_frame = ttk.Frame(selection_panel)
        self.card_selection_frame.pack(pady=5)
        
        # Crear mini-deck
        self.create_mini_deck()
    
    def create_mini_deck(self):
        """Crea el mini-deck para seleccionar cartas"""
        # Frame contenedor para el mini-deck
        deck_container = ttk.Frame(self.card_selection_frame)
        deck_container.pack()
        
        # Organizar por palos en un grid 2x2
        suits = [("s", "PICAS ♠", "white"), ("h", "CORAZONES ♥", "red"), 
                ("d", "DIAMANTES ♦", "red"), ("c", "TRÉBOLES ♣", "white")]
        
        # Crear un grid 2x2 para los palos
        for idx, (suit, name, color) in enumerate(suits):
            # Frame para cada palo
            suit_frame = ttk.Frame(deck_container)
            suit_frame.grid(row=idx//2, column=idx%2, padx=5, pady=3)
            
            # Etiqueta del palo
            suit_label = ttk.Label(suit_frame, text=name, 
                                  foreground=color, background="#05422b",
                                  font=("Arial", 9, "bold"))
            suit_label.pack(pady=(0, 2))
            
            # Grid para las cartas del palo
            cards_grid = ttk.Frame(suit_frame)
            cards_grid.pack()
            
            # Crear botones para cada carta del palo
            ranks = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
            
            # Organizar las cartas en una cuadrícula
            for i, rank in enumerate(ranks):
                card = f"{rank}{suit}"
                
                # Frame para contener el botón de la carta
                card_frame = ttk.Frame(cards_grid)
                card_frame.grid(row=i//7, column=i%7, padx=1, pady=1)
                
                # Botón para la carta
                button = self.create_card_button(card_frame, rank, suit, card)
                
                # Guardar referencia al botón
                self.card_buttons[card] = button
    
    def create_card_button(self, parent, rank, suit, card):
        """Crea un botón para representar una carta"""
        # Crear un botón con aspecto de carta de póker
        color = "red" if suit in ["h", "d"] else "black"
        
        # Canvas para la carta
        card_canvas = tk.Canvas(parent, width=30, height=30, bg="#ffffff", highlightthickness=1, 
                              highlightbackground="#000000")
        card_canvas.pack()
        
        # Dibujar el rango y el símbolo
        suit_symbol = self.get_suit_symbol(suit)
        card_canvas.create_text(8, 8, text=rank, fill=color, font=("Arial", 9, "bold"))
        card_canvas.create_text(22, 22, text=suit_symbol, fill=color, font=("Arial", 10))
        
        # Hacer clic en la carta para seleccionarla
        card_canvas.bind("<Button-1>", lambda e, c=card: self.select_card(c))
        
        return card_canvas
    
    def create_controls_section(self, parent):
        """Crea la sección de controles y resultados"""
        bottom_panel = ttk.Frame(parent)
        bottom_panel.pack(fill=tk.X, pady=5)
        
        # Dividir en dos columnas
        controls_frame = ttk.Frame(bottom_panel)
        controls_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        results_frame = ttk.Frame(bottom_panel)
        results_frame.pack(side=tk.RIGHT, padx=(10, 0), fill=tk.X, expand=True)
        
        # Control para número de oponentes
        opponents_frame = ttk.Frame(controls_frame)
        opponents_frame.pack(pady=5)
        
        opponents_label = ttk.Label(opponents_frame, text="Oponentes:", style="TLabel")
        opponents_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.opponents_var = tk.StringVar(value="1")
        opponents_spinbox = ttk.Spinbox(opponents_frame, from_=1, to=9, width=3, textvariable=self.opponents_var)
        opponents_spinbox.pack(side=tk.LEFT)
        
        # Configurar evento para cuando cambia el número de oponentes
        opponents_spinbox.bind("<<Increment>>", lambda e: self.on_opponents_change())
        opponents_spinbox.bind("<<Decrement>>", lambda e: self.on_opponents_change())
        
        # Botones
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(pady=5)
        
        calculate_button = ttk.Button(buttons_frame, text="CALCULAR", 
                                     command=self.calculate_odds, style="TButton",
                                     width=15)
        calculate_button.pack(pady=(0, 5))
        
        reset_button = ttk.Button(buttons_frame, text="REINICIAR", 
                                 command=self.reset, style="TButton",
                                 width=15)
        reset_button.pack()
        
        # El botón de consejo AI solo se muestra si no hay configuración de IA
        if not self.ai_clients:
            # Botón para pedir consejo AI manualmente (solo si no hay configuración automática)
            ai_advice_button = ttk.Button(buttons_frame, text="CONSEJO AI",
                                      command=self.get_ai_advice, style="TButton",
                                      width=15)
            ai_advice_button.pack(pady=(5, 0))
        
        # Marco para resultados
        results_container = ttk.Frame(results_frame)
        results_container.pack(pady=5, fill=tk.X)
        
        self.status_label = ttk.Label(results_container, 
                                     text="Selecciona tus cartas para calcular probabilidades", 
                                     foreground="#ffd700", background="#05422b", wraplength=300)
        self.status_label.pack(pady=(0, 5), fill=tk.X)
        
        self.win_probability_label = ttk.Label(results_container, 
                                             text="Probabilidad de ganar: -", 
                                             style="Result.TLabel")
        self.win_probability_label.pack(pady=2, fill=tk.X)
        
        self.hand_strength_label = ttk.Label(results_container, 
                                           text="Fuerza de la mano: -", 
                                           style="Result.TLabel")
        self.hand_strength_label.pack(pady=2, fill=tk.X)
    
    def create_recommendations_section(self, parent):
        """Crea la sección de recomendaciones"""
        recommendation_frame = ttk.Frame(parent)
        recommendation_frame.pack(fill=tk.X, pady=5)
        
        recommendation_title = ttk.Label(recommendation_frame, text="GUÍA DE RECOMENDACIONES", 
                                      style="Subheader.TLabel")
        recommendation_title.pack(pady=(5, 2))
        
        # Crear un frame con borde para destacar las recomendaciones
        rec_border = ttk.Frame(recommendation_frame, style="TFrame")
        rec_border.pack(fill=tk.X, pady=5)
        
        # Añadir un borde visual usando un canvas
        rec_canvas = tk.Canvas(rec_border, bg="#05422b", highlightbackground="#ffd700", 
                             highlightthickness=2, height=120)
        rec_canvas.pack(fill=tk.X, expand=True)
        
        recommendations = [
            ">60%: Apuesta fuerte o aumenta. Mano dominante.",
            "40-60%: Continúa con confianza. Buenos odds.",
            "25-40%: Juega con precaución. Valora el bote.",
            "<25%: Retírate a menos que el farol sea viable."
        ]
        
        # Añadir recomendaciones al canvas
        y_pos = 15
        for rec in recommendations:
            rec_canvas.create_text(10, y_pos, text=rec, fill="#ffd700", font=("Arial", 9),
                                 anchor=tk.W)
            y_pos += 25
    
    def create_ai_advice_section(self, parent):
        """Crea la sección para mostrar consejos de IA y chat"""
        ai_advice_frame = ttk.Frame(parent)
        ai_advice_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ai_advice_header = ttk.Label(ai_advice_frame, text="CONSEJOS DE INTELIGENCIA ARTIFICIAL", 
                                    style="Subheader.TLabel")
        ai_advice_header.pack(pady=(5, 2))
        
        # Texto para mostrar consejos de IA y chat combinados en un solo área
        self.ai_advice_text = tk.Text(ai_advice_frame, height=15, width=40, bg="#083d1e", fg="white",
                                   font=("Arial", 9), wrap=tk.WORD)
        self.ai_advice_text.pack(pady=5, fill=tk.BOTH, expand=True)
        self.ai_advice_text.config(state=tk.DISABLED)
        
        # Scrollbar para el área de texto
        scrollbar = ttk.Scrollbar(self.ai_advice_text, command=self.ai_advice_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ai_advice_text.config(yscrollcommand=scrollbar.set)
        
        # Inicializar texto
        self.update_ai_advice_text("Los consejos de IA aparecerán aquí. Selecciona tus cartas para recibir análisis automático.")
        
        # Sección de chat integrada en la parte inferior
        chat_section = ttk.Frame(parent)
        chat_section.pack(fill=tk.X, pady=(5, 0))
        
        chat_label = ttk.Label(chat_section, text="CHAT CON LA IA", style="Subheader.TLabel")
        chat_label.pack(pady=(5, 5))
        
        # Frame para entrada de texto y botón
        chat_input_frame = ttk.Frame(chat_section)
        chat_input_frame.pack(fill=tk.X)
        
        # Entry para ingresar preguntas
        self.chat_entry = tk.Entry(chat_input_frame, bg="#0a4728", fg="white", font=("Arial", 9))
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_entry.insert(0, "Escribe tu pregunta sobre la situación actual...")
        self.chat_entry.bind("<FocusIn>", self.clear_entry_placeholder)
        self.chat_entry.bind("<Return>", self.send_chat_message)
        
        # Botón enviar
        send_button = ttk.Button(chat_input_frame, text="Preguntar", 
                              command=self.send_chat_message, width=10)
        send_button.pack(side=tk.RIGHT)
        
        # Etiquetas de ejemplo de preguntas
        examples_frame = ttk.Frame(chat_section)
        examples_frame.pack(fill=tk.X, pady=(5, 0))
        
        examples_label = ttk.Label(examples_frame, text="Ejemplos: ", foreground="#ffd700", 
                                background="#05422b", font=("Arial", 8))
        examples_label.pack(side=tk.LEFT, padx=(0, 5))
        
        example_questions = [
            "¿Qué hacer si el oponente va all-in?",
            "Si muestran fuerza, ¿debo retroceder?",
            "¿Cuánto apostar con esta mano?"
        ]
        
        for i, question in enumerate(example_questions):
            q_label = ttk.Label(examples_frame, text=question, foreground="#aaaaaa", 
                             background="#05422b", font=("Arial", 8))
            q_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Agregar evento de clic para cargar la pregunta en el entry
            q_label.bind("<Button-1>", lambda e, q=question: self.load_example_question(q))
    
    #----------------------------------------
    # Métodos para manipular cartas
    #----------------------------------------
    
    def select_card(self, card):
        """Maneja la selección/deselección de una carta"""
        # Validar que la carta seleccionada existe y no está ya seleccionada
        all_selected = self.hand_cards + self.table_cards
        
        if card in all_selected:
            # Si la carta ya está seleccionada, quitarla
            if card in self.hand_cards:
                self.hand_cards.remove(card)
                self.show_status(f"Carta {card} eliminada de tu mano")
            elif card in self.table_cards:
                self.table_cards.remove(card)
                self.show_status(f"Carta {card} eliminada de la mesa")
        else:
            # Si no está seleccionada, añadirla según corresponda
            if len(self.hand_cards) < 2:
                self.hand_cards.append(card)
                remaining = 2 - len(self.hand_cards)
                if remaining > 0:
                    self.show_status(f"{card} añadida a tu mano. Falta {remaining} carta")
                else:
                    self.show_status("Mano completa. Selecciona cartas comunitarias")
            elif len(self.table_cards) < 5:
                self.table_cards.append(card)
                remaining = 5 - len(self.table_cards)
                if remaining > 0:
                    self.show_status(f"{card} añadida a la mesa. Faltan {remaining} cartas")
                else:
                    self.show_status("Todas las cartas seleccionadas. Calcula probabilidades")
            else:
                self.show_status("Ya seleccionaste todas las cartas posibles")
        
        # Actualizar visualización
        self.update_card_display()
        
        # Calcular probabilidad y obtener consejo automáticamente cada vez que cambia el estado
        if len(self.hand_cards) == 2:
            self.calculate_preliminary_odds()
            
            # Solicitar consejo de IA automáticamente si hay modelos disponibles
            if self.ai_clients:
                self.get_ai_advice(automatic=True)
    
    def update_card_display(self):
        """Actualiza la visualización de las cartas seleccionadas"""
        # Actualizar visualización de cartas y destacar seleccionadas
        
        # Restablecer estilos de todos los botones
        for card_id, button in self.card_buttons.items():
            button.config(highlightbackground="#000000", highlightthickness=1)
        
        # Destacar cartas seleccionadas en el mini-deck
        for card in self.hand_cards:
            if card in self.card_buttons:
                self.card_buttons[card].config(highlightbackground="#ff9900", highlightthickness=2)
        
        for card in self.table_cards:
            if card in self.card_buttons:
                self.card_buttons[card].config(highlightbackground="#3399ff", highlightthickness=2)
        
        # Limpiar y actualizar cartas de la mano
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
            
        # Limpiar y actualizar cartas comunitarias
        for widget in self.community_frame.winfo_children():
            widget.destroy()
        
        # Mostrar cartas de la mano
        for card in self.hand_cards:
            self.display_card(self.hand_frame, card, "player")
        
        # Mostrar slots vacíos para completar la mano
        for _ in range(2 - len(self.hand_cards)):
            self.display_empty_slot(self.hand_frame, "player")
            
        # Mostrar cartas comunitarias
        for card in self.table_cards:
            self.display_card(self.community_frame, card, "community")
            
        # Mostrar slots vacíos para completar la mesa
        for _ in range(5 - len(self.table_cards)):
            self.display_empty_slot(self.community_frame, "community")
            
        # Si cambió el estado de la mesa y tenemos la mano completa, 
        # solicitar consejo de IA automáticamente
        if len(self.hand_cards) == 2 and self.table_cards and self.ai_clients:
            self.get_ai_advice(automatic=True)
    
    def display_card(self, parent, card, location="player"):
        """Crea una visualización de una carta en la interfaz"""
        # Crear un frame para la carta
        if location == "player":
            card_width, card_height = 70, 100
        else:
            card_width, card_height = 50, 70
            
        card_frame = ttk.Frame(parent, width=card_width, height=card_height)
        card_frame.pack(side=tk.LEFT, padx=2)
        card_frame.pack_propagate(False)
        
        # Canvas para dibujar la carta
        card_canvas = tk.Canvas(card_frame, width=card_width, height=card_height, 
                              bg="white", highlightthickness=1, highlightbackground="black")
        card_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Obtener rango y palo
        rank = card[0]
        suit = card[1]
        suit_symbol = self.get_suit_symbol(suit)
        color = "red" if suit in ["h", "d"] else "black"
        
        # Dibujar rango en las esquinas
        font_size = 14 if location == "player" else 12
        corner_offset = 10 if location == "player" else 8
        
        card_canvas.create_text(corner_offset, corner_offset, text=rank, 
                              font=("Arial", font_size, "bold"), fill=color)
        
        card_canvas.create_text(card_width-corner_offset, corner_offset, text=suit_symbol, 
                              font=("Arial", font_size), fill=color)
        
        # Dibujar símbolo grande en el centro
        center_font_size = 36 if location == "player" else 28
        card_canvas.create_text(card_width/2, card_height/2, text=suit_symbol, 
                              font=("Arial", center_font_size), fill=color)
        
        # Dibujar rango y palo invertidos en la esquina inferior
        card_canvas.create_text(card_width-corner_offset, card_height-corner_offset, 
                              text=rank, font=("Arial", font_size, "bold"), fill=color)
        
        card_canvas.create_text(corner_offset, card_height-corner_offset, 
                              text=suit_symbol, font=("Arial", font_size), fill=color)
    
    def display_empty_slot(self, parent, location="community"):
        """Crea un slot vacío para una carta"""
        # Crear un frame vacío para representar un slot de carta
        if location == "player":
            slot_width, slot_height = 70, 100
        else:
            slot_width, slot_height = 50, 70
            
        slot_frame = ttk.Frame(parent, width=slot_width, height=slot_height)
        slot_frame.pack(side=tk.LEFT, padx=2)
        slot_frame.pack_propagate(False)
        
        # Canvas para el slot vacío
        slot_canvas = tk.Canvas(slot_frame, width=slot_width, height=slot_height, 
                              bg="#083d1e", highlightthickness=1, highlightbackground="#666666")
        slot_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Dibujar borde punteado
        slot_canvas.create_rectangle(2, 2, slot_width-2, slot_height-2, 
                                   outline="#666666", dash=(2, 2), fill="#083d1e")
        
        # Mostrar signo de interrogación
        slot_canvas.create_text(slot_width/2, slot_height/2, text="?", 
                              font=("Arial", 20), fill="#666666")
    
    def get_suit_symbol(self, suit):
        """Obtiene el símbolo correspondiente a un palo"""
        symbols = {"c": "♣", "d": "♦", "h": "♥", "s": "♠"}
        return symbols.get(suit, suit)
    
    #----------------------------------------
    # Métodos de cálculo de probabilidades
    #----------------------------------------
    
    def calculate_preliminary_odds(self):
        """Cálculo rápido para actualizar las probabilidades iniciales"""
        if len(self.hand_cards) == 2:
            available_cards = [card for card in self.all_cards if card not in self.hand_cards and card not in self.table_cards]
            win_probability, hand_strength = self.monte_carlo_simulation(available_cards, 100)
            
            self.win_probability_label.config(text=f"Probabilidad de ganar: {win_probability:.2f}%")
            self.hand_strength_label.config(text=f"Fuerza de la mano: {hand_strength}")
            
            # Añadir recomendación básica según probabilidad
            if win_probability > 60:
                self.show_status("Buena mano inicial. Considerar apostar.")
            elif win_probability > 40:
                self.show_status("Mano inicial aceptable. Jugar con cautela.")
            elif win_probability > 25:
                self.show_status("Mano inicial débil. Revisar solo si es barato.")
            else:
                self.show_status("Mano inicial muy débil. Mejor retirarse temprano.")
    
    def calculate_odds(self):
        """Calcula las probabilidades de ganar con la mano actual"""
        # Verificar que hay suficientes cartas seleccionadas
        if len(self.hand_cards) != 2:
            self.show_status("Error: Debes seleccionar exactamente 2 cartas para tu mano")
            return
        
        try:
            self.opponents = int(self.opponents_var.get())
            if self.opponents < 1:
                self.opponents = 1
            elif self.opponents > 9:
                self.opponents = 9
        except ValueError:
            self.opponents = 1
        
        # Mostrar mensaje de cálculo
        self.show_status("Calculando probabilidades... Por favor espera")
        self.root.update()
        
        # Cartas disponibles
        available_cards = [card for card in self.all_cards if card not in self.hand_cards and card not in self.table_cards]
        
        # Realizar simulación Monte Carlo
        num_simulations = 1000
        win_probability, hand_strength = self.monte_carlo_simulation(available_cards, num_simulations)
        
        # Mostrar resultados
        self.win_probability_label.config(text=f"Probabilidad de ganar: {win_probability:.2f}%")
        self.hand_strength_label.config(text=f"Fuerza de la mano: {hand_strength}")
        
        # Mensaje descriptivo basado en la probabilidad
        if win_probability > 80:
            message = "¡EXCELENTE MANO! Altas probabilidades de ganar."
            recommendation = "RECOMENDACIÓN: Apuesta fuerte o sube las apuestas."
        elif win_probability > 60:
            message = "BUENA MANO. Tienes ventaja sobre tus oponentes."
            recommendation = "RECOMENDACIÓN: Apuesta con confianza, considera aumentar."
        elif win_probability > 40:
            message = "MANO DECENTE. Probabilidades razonables."
            recommendation = "RECOMENDACIÓN: Continúa con precaución, valora el bote."
        elif win_probability > 25:
            message = "MANO DÉBIL. Juega con precaución."
            recommendation = "RECOMENDACIÓN: Revisa solo si es barato o posible farol."
        else:
            message = "MANO MUY DÉBIL. Considera retirarte."
            recommendation = "RECOMENDACIÓN: Mejor retirarse a menos que el farol sea viable."
            
        self.show_status(f"{message} {recommendation} (vs {self.opponents} oponente{'s' if self.opponents > 1 else ''})")
        
        # Solicitar consejo de IA automáticamente después del cálculo
        if self.ai_clients:
            self.get_ai_advice(automatic=True)
    
    def monte_carlo_simulation(self, available_cards, num_simulations=1000):
        """Realiza una simulación Monte Carlo para calcular probabilidades"""
        # Simulación Monte Carlo para calcular probabilidades
        wins = 0
        hand_type_counts = {"High Card": 0, "Pair": 0, "Two Pair": 0, "Three of a Kind": 0, 
                           "Straight": 0, "Flush": 0, "Full House": 0, "Four of a Kind": 0, 
                           "Straight Flush": 0, "Royal Flush": 0}
        
        for _ in range(num_simulations):
            # Cartas comunitarias restantes a repartir
            remaining_community = 5 - len(self.table_cards)
            
            # Barajar las cartas disponibles
            simulation_deck = available_cards.copy()
            random.shuffle(simulation_deck)
            
            # Completar las cartas comunitarias para esta simulación
            simulation_community = self.table_cards.copy()
            simulation_community.extend(simulation_deck[:remaining_community])
            
            # Generar manos para los oponentes
            opponent_hands = []
            cards_used = 0
            for i in range(self.opponents):
                opponent_hand = simulation_deck[remaining_community + cards_used:remaining_community + cards_used + 2]
                cards_used += 2
                if len(opponent_hand) == 2:  # Asegurarse de que haya suficientes cartas
                    opponent_hands.append(opponent_hand)
            
            # Evaluar la mano del jugador
            player_score, player_hand_type = self.evaluate_hand(self.hand_cards, simulation_community)
            hand_type_counts[player_hand_type] += 1
            
            # Evaluar las manos de los oponentes
            player_wins = True
            for opponent_hand in opponent_hands:
                opponent_score, _ = self.evaluate_hand(opponent_hand, simulation_community)
                if opponent_score >= player_score:
                    player_wins = False
                    break
            
            if player_wins:
                wins += 1
        
        # Calcular probabilidad de ganar
        win_probability = (wins / num_simulations) * 100
        
        # Determinar la mano más común
        most_common_hand = max(hand_type_counts.items(), key=lambda x: x[1])[0]
        
        # Traducir el tipo de mano al español
        hand_translations = {
            "High Card": "Carta Alta",
            "Pair": "Par",
            "Two Pair": "Doble Par",
            "Three of a Kind": "Trio",
            "Straight": "Escalera",
            "Flush": "Color",
            "Full House": "Full House",
            "Four of a Kind": "Poker",
            "Straight Flush": "Escalera de Color",
            "Royal Flush": "Escalera Real"
        }
        
        translated_hand = hand_translations.get(most_common_hand, most_common_hand)
        
        return win_probability, translated_hand
    
    def evaluate_hand(self, hole_cards, community_cards):
        """Evalúa la fuerza de una mano de poker"""
        # Combinar las cartas de la mano y comunitarias
        all_cards = hole_cards + community_cards
        
        # Convertir representaciones de cartas a valores numéricos
        values = []
        suits = []
        for card in all_cards:
            rank = card[0]
            suit = card[1]
            
            # Convertir rango a valor numérico
            if rank == "T":
                value = 10
            elif rank == "J":
                value = 11
            elif rank == "Q":
                value = 12
            elif rank == "K":
                value = 13
            elif rank == "A":
                value = 14
            else:
                value = int(rank)
            
            values.append(value)
            suits.append(suit)
        
        # Ordenar valores
        values.sort(reverse=True)
        
        # Verificar manos posibles
        
        # Royal Flush
        if self.is_straight_flush(values, suits) and 14 in values:
            return 9, "Royal Flush"
        
        # Straight Flush
        if self.is_straight_flush(values, suits):
            return 8, "Straight Flush"
        
        # Four of a Kind
        if self.is_four_of_a_kind(values):
            return 7, "Four of a Kind"
        
        # Full House
        if self.is_full_house(values):
            return 6, "Full House"
        
        # Flush
        if self.is_flush(suits):
            return 5, "Flush"
        
        # Straight
        if self.is_straight(values):
            return 4, "Straight"
        
        # Three of a Kind
        if self.is_three_of_a_kind(values):
            return 3, "Three of a Kind"
        
        # Two Pair
        if self.is_two_pair(values):
            return 2, "Two Pair"
        
        # Pair
        if self.is_pair(values):
            return 1, "Pair"
        
        # High Card
        return 0, "High Card"
    
    def is_straight_flush(self, values, suits):
        """Verifica si hay una escalera de color"""
        return self.is_straight(values) and self.is_flush(suits)
    
    def is_four_of_a_kind(self, values):
        """Verifica si hay cuatro del mismo valor"""
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        return 4 in value_counts.values()
    
    def is_full_house(self, values):
        """Verifica si hay un full house"""
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        return 3 in value_counts.values() and 2 in value_counts.values()
    
    def is_flush(self, suits):
        """Verifica si hay un color"""
        suit_counts = {}
        for suit in suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        return max(suit_counts.values()) >= 5
    
    def is_straight(self, values):
        """Verifica si hay una escalera"""
        # Eliminar duplicados y ordenar
        unique_values = sorted(set(values), reverse=True)
        
        # Considerar el As como un 1 para straight A-5
        if 14 in unique_values:
            unique_values.append(1)
        
        # Buscar 5 valores consecutivos
        for i in range(len(unique_values) - 4):
            if unique_values[i] - unique_values[i + 4] == 4:
                return True
        
        return False
    
    def is_three_of_a_kind(self, values):
        """Verifica si hay tres del mismo valor"""
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        return 3 in value_counts.values()
    
    def is_two_pair(self, values):
        """Verifica si hay dos pares"""
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        pairs = [value for value, count in value_counts.items() if count == 2]
        return len(pairs) >= 2
    
    def is_pair(self, values):
        """Verifica si hay un par"""
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        return 2 in value_counts.values()
    
    #----------------------------------------
    # Métodos para consejos de IA
    #----------------------------------------
    
    def update_ai_advice_text(self, text):
        """Actualiza el área de texto con consejos de IA"""
        self.ai_advice_text.config(state=tk.NORMAL)
        self.ai_advice_text.delete(1.0, tk.END)
        self.ai_advice_text.insert(tk.END, text)
        self.ai_advice_text.config(state=tk.DISABLED)
    
    def get_ai_advice(self, automatic=False):
        """Consulta a múltiples modelos de IA para obtener consejos sobre la mano actual"""
        # Verificar que hay suficientes cartas seleccionadas
        if len(self.hand_cards) != 2:
            if not automatic:  # Solo mostrar error si fue solicitud manual
                self.update_ai_advice_text("Error: Necesitas seleccionar tus 2 cartas primero.")
            return
            
        # Verificar que hay modelos de IA disponibles
        if not self.ai_clients:
            if not automatic:  # Solo mostrar error si fue solicitud manual
                self.update_ai_advice_text("No hay modelos de IA configurados o disponibles.")
            return
            
        # Crear la descripción de la situación actual
        hand_description = self.format_cards_for_ai(self.hand_cards)
        table_description = self.format_cards_for_ai(self.table_cards)
        opponents_count = self.opponents_var.get()
        
        # Mostrar estado de procesamiento
        if automatic:
            if "Los consejos de IA aparecerán aquí" in self.ai_advice_text.get("1.0", tk.END):
                # Si es la primera vez, reemplazar el texto inicial
                self.update_ai_advice_text("Consultando AI para analizar la jugada...")
            else:
                # Si ya hay contenido, añadir mensaje de actualización al final
                self.append_ai_text("\n\nActualizando análisis...")
        else:
            self.update_ai_advice_text("Consultando a los modelos de IA... Por favor espera.")
        self.root.update()
        
        # Crear el prompt para la IA
        prompt = f"""
        Eres un experto en póker Texas Hold'em. Analiza esta situación y da un consejo estratégico:
        
        Mi mano: {hand_description}
        Cartas comunitarias: {table_description if table_description else "Ninguna carta en la mesa todavía"}
        Número de oponentes: {opponents_count}
        
        Responde en 3 puntos numerados y concisos (máximo 2 líneas cada uno):
        1. Evaluación de la fuerza de la mano actual
        2. Probabilidades de mejorar (si aplica)
        3. Recomendación estratégica específica para esta situación
        """
        
        # Ejecutar las consultas en un hilo separado para no bloquear la interfaz
        threading.Thread(target=self.run_ai_queries, args=(prompt, automatic)).start()
    
    def run_ai_queries(self, prompt, automatic=False):
        """Ejecuta consultas a múltiples modelos de IA y combina sus respuestas"""
        all_responses = {}
        
        # Consultar a cada modelo disponible
        for model_name, client in self.ai_clients.items():
            try:
                # Obtener configuración del modelo
                model_config = self.ai_models[model_name]
                model_id = model_config["model"]
                
                # Realizar la consulta según el tipo de API
                if model_config["api_type"] == "openai":
                    response = client.chat.completions.create(
                        model=model_id,
                        messages=[
                            {"role": "system", "content": "Eres un experto en póker que da consejos concisos y estratégicos."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=200
                    )
                    advice = response.choices[0].message.content
                    all_responses[model_name] = {
                        "text": advice,
                        "weight": model_config.get("weight", 1.0)
                    }
                    
                    # Actualizar el área de texto con progreso si no es automático
                    if not automatic:
                        self.root.after(0, lambda: self.update_ai_progress(f"Consultando modelos... ({len(all_responses)}/{len(self.ai_clients)})"))
            
            except Exception as e:
                print(f"Error consultando al modelo {model_name}: {e}")
        
        # Combinar todas las respuestas
        if all_responses:
            # Si solo hay un modelo, mostrar directamente su respuesta sin formato adicional
            if len(all_responses) == 1 or automatic:
                # Con un solo modelo o en modo automático, mostramos directamente la respuesta
                model_name = list(all_responses.keys())[0]
                advice_text = all_responses[model_name]["text"]
                self.root.after(0, lambda: self.update_ai_advice_text(advice_text))
            else:
                # Con múltiples modelos y solicitud manual, mostramos el formato completo con consenso
                combined_advice = self.combine_ai_responses(all_responses)
                self.root.after(0, lambda: self.update_ai_advice_text(combined_advice))
        else:
            if not automatic:  # Solo mostrar error si no es automático
                self.root.after(0, lambda: self.update_ai_advice_text("No se pudo obtener consejos de los modelos de IA."))
    
    def update_ai_progress(self, message):
        """Actualiza el progreso de las consultas de IA"""
        self.update_ai_advice_text(message)
    
    def combine_ai_responses(self, responses):
        """Combina las respuestas de múltiples modelos según sus pesos"""
        if not responses:
            return "No se recibieron respuestas de los modelos."
            
        combined_text = "CONSEJOS DE LOS MODELOS:\n\n"
        
        # Añadir respuesta de cada modelo
        for model_name, response_data in responses.items():
            combined_text += f"--- {model_name.upper()} ---\n"
            combined_text += response_data["text"] + "\n\n"
        
        # Si hay más de un modelo, añadir un resumen consensuado
        if len(responses) > 1:
            combined_text += "--- CONSENSO ---\n"
            combined_text += "Los modelos coinciden en recomendar: "
            # Aquí podríamos implementar un algoritmo más sofisticado para extraer el consenso
            # Por simplicidad, usamos la respuesta del modelo con mayor peso
            best_model = max(responses.items(), key=lambda x: x[1]["weight"])
            combined_text += self.extract_recommendation(best_model[1]["text"])
            
        return combined_text
    
    def extract_recommendation(self, text):
        """Extrae la recomendación principal de un texto de consejo"""
        # Implementación simple: tomar la última oración o buscar frases clave
        sentences = text.split('.')
        if sentences:
            for sentence in reversed(sentences):
                if "recomend" in sentence.lower() or "deberías" in sentence.lower() or "sugiero" in sentence.lower():
                    return sentence.strip() + "."
            # Si no encontramos frases clave, devolver la última oración con contenido
            for sentence in reversed(sentences):
                if len(sentence.strip()) > 10:
                    return sentence.strip() + "."
        return text
    
    def format_cards_for_ai(self, cards):
        """Formatea las cartas para que sean legibles por la IA"""
        if not cards:
            return ""
            
        formatted_cards = []
        rank_names = {
            "A": "As", 
            "K": "Rey", 
            "Q": "Reina", 
            "J": "Jota", 
            "T": "10"
        }
        suit_names = {
            "c": "Tréboles",
            "d": "Diamantes",
            "h": "Corazones",
            "s": "Picas"
        }
        
        for card in cards:
            rank = card[0]
            suit = card[1]
            
            rank_name = rank_names.get(rank, rank)
            suit_name = suit_names.get(suit, suit)
            
            formatted_cards.append(f"{rank_name} de {suit_name}")
            
        return ", ".join(formatted_cards)
    
    #----------------------------------------
    # Métodos de chat con IA
    #----------------------------------------
    
    def clear_entry_placeholder(self, event):
        """Limpia el placeholder del campo de entrada cuando se hace clic"""
        if self.chat_entry.get() == "Escribe tu pregunta sobre la situación actual...":
            self.chat_entry.delete(0, tk.END)
    
    def load_example_question(self, question):
        """Carga una pregunta de ejemplo en el campo de entrada"""
        self.chat_entry.delete(0, tk.END)
        self.chat_entry.insert(0, question)
        self.chat_entry.focus_set()
    
    def send_chat_message(self, event=None):
        """Envía un mensaje de chat a la IA"""
        # Obtener mensaje
        message = self.chat_entry.get().strip()
        
        # Verificar que no está vacío y no es el placeholder
        if not message or message == "Escribe tu pregunta sobre la situación actual...":
            return
            
        # Agregar mensaje del usuario al área de consejos de IA
        current_text = self.ai_advice_text.get("1.0", tk.END)
        self.update_ai_advice_text(current_text + f"\n\nTú: {message}")
        
        # Limpiar entrada
        self.chat_entry.delete(0, tk.END)
        
        # Si no hay IA configurada, mostrar mensaje de error
        if not self.ai_clients:
            self.append_ai_text("IA: No hay modelos de IA configurados. Por favor configura un modelo para chatear.")
            return
            
        # Mostrar indicador de espera
        self.append_ai_text("IA: Pensando...")
        self.root.update()
        
        # Crear contexto para la IA basado en el estado actual del juego
        hand_description = self.format_cards_for_ai(self.hand_cards) if self.hand_cards else "No has seleccionado cartas de mano"
        table_description = self.format_cards_for_ai(self.table_cards) if self.table_cards else "No hay cartas en la mesa"
        
        # Información sobre la probabilidad calculada
        probability_info = ""
        if hasattr(self, 'win_probability_label'):
            probability_text = self.win_probability_label.cget("text")
            if ":" in probability_text:
                probability_info = f"Probabilidad de ganar: {probability_text.split(':')[1].strip()}"
        
        # Obtener el historial de conversación previo (últimos 5 intercambios)
        conversation_history = self.extract_conversation_history()
        
        # Construir el prompt de contexto con historial
        context = f"""
        Como experto en póker, responde a la siguiente pregunta de forma breve y directa.
        
        CONTEXTO ACTUAL DEL JUEGO:
        - Mano del jugador: {hand_description}
        - Mesa: {table_description}
        - Oponentes: {self.opponents_var.get()}
        - {probability_info}
        
        HISTORIAL DE CONVERSACIÓN RECIENTE:
        {conversation_history}
        
        PREGUNTA ACTUAL DEL JUGADOR: {message}
        
        Responde de manera concisa (máximo 3 líneas) con un consejo estratégico específico para esta situación.
        Toma en cuenta el historial de conversación para dar una respuesta coherente.
        """
        
        # Enviar en un hilo separado para no bloquear la interfaz
        threading.Thread(target=self.process_chat_message, args=(context,)).start()
    
    def extract_conversation_history(self):
        """Extrae el historial de conversación de chat del área de consejos"""
        # Obtener todo el texto del área
        all_text = self.ai_advice_text.get("1.0", tk.END)
        
        # Buscar todos los intercambios de chat (Tú: ... IA: ...)
        chat_lines = []
        lines = all_text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("Tú:"):
                # Encontrar la respuesta de IA que le corresponde
                user_message = line
                ia_response = ""
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith("IA:"):
                        ia_response = lines[j].strip()
                        i = j  # Actualizar índice para continuar desde aquí
                        break
                if user_message and ia_response:
                    chat_lines.append(user_message)
                    chat_lines.append(ia_response)
            i += 1
        
        # Limitar a los últimos 5 intercambios (10 líneas: pregunta + respuesta)
        if len(chat_lines) > 10:
            chat_lines = chat_lines[-10:]
        
        return "\n".join(chat_lines)
    
    def process_chat_message(self, prompt):
        """Procesa el mensaje de chat enviándolo a la IA y mostrando la respuesta"""
        try:
            # Tomar el primer modelo disponible para el chat
            model_name = list(self.ai_clients.keys())[0]
            client = self.ai_clients[model_name]
            model_config = self.ai_models[model_name]
            model_id = model_config["model"]
            
            # Consulta al modelo
            if model_config["api_type"] == "openai":
                # Crear un array de mensajes para mantener el contexto conversacional
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": "Eres un experto en póker que da consejos concisos y estratégicos. Mantén el contexto conversacional y responde apropiadamente basándote en el historial de la conversación."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                advice = response.choices[0].message.content
                
                # Actualizar área de consejos y reemplazar mensaje de "Pensando..."
                self.root.after(0, lambda: self.replace_thinking_text(f"IA: {advice}"))
            
        except Exception as e:
            print(f"Error al procesar mensaje de chat: {e}")
            self.root.after(0, lambda: self.replace_thinking_text(f"IA: Lo siento, hubo un error al procesar tu pregunta."))
    
    def append_ai_text(self, text):
        """Añade texto al área de consejos de IA sin eliminar el contenido previo"""
        self.ai_advice_text.config(state=tk.NORMAL)
        if self.ai_advice_text.get("1.0", tk.END).strip():
            self.ai_advice_text.insert(tk.END, "\n\n")
        self.ai_advice_text.insert(tk.END, text)
        self.ai_advice_text.see(tk.END)  # Scroll al final
        self.ai_advice_text.config(state=tk.DISABLED)
    
    def replace_thinking_text(self, text):
        """Reemplaza el último mensaje 'IA: Pensando...' con la respuesta real"""
        self.ai_advice_text.config(state=tk.NORMAL)
        
        # Buscar último mensaje "IA: Pensando..."
        content = self.ai_advice_text.get("1.0", tk.END)
        if "IA: Pensando..." in content:
            # Encontrar la última ocurrencia
            last_thinking = content.rindex("IA: Pensando...")
            
            # Encontrar el final de la línea o el final del texto
            end_line = content.find("\n", last_thinking)
            if end_line == -1:  # Si no hay salto de línea, usar el final del texto
                end_line = len(content)
            
            # Borrar desde la posición de "IA: Pensando..." hasta el final de esa línea
            self.ai_advice_text.delete(f"1.0 + {last_thinking}c", f"1.0 + {end_line}c")
            
            # Insertar el nuevo texto
            self.ai_advice_text.insert(f"1.0 + {last_thinking}c", text)
        else:
            # Si no encontramos el mensaje de pensando, solo agregamos el nuevo
            self.append_ai_text(text)
            
        self.ai_advice_text.see(tk.END)  # Scroll al final
        self.ai_advice_text.config(state=tk.DISABLED)
    
    #----------------------------------------
    # Eventos de cambio de estado
    #----------------------------------------
    
    def on_opponents_change(self):
        """Manejador para cuando cambia el número de oponentes"""
        # Si tenemos cartas de mano y configuración AI, actualizar consejo
        if len(self.hand_cards) == 2 and self.ai_clients:
            # Esperar un momento para que el valor se actualice
            self.root.after(100, lambda: self.get_ai_advice(automatic=True))
    
    #----------------------------------------
    # Métodos misceláneos
    #----------------------------------------
    
    def show_status(self, message):
        """Actualiza el mensaje de estado en la interfaz"""
        self.status_label.config(text=message)
    
    def reset(self):
        """Reinicia la aplicación a su estado inicial"""
        # Reiniciar variables
        self.hand_cards = []
        self.table_cards = []
        
        # Limpiar visualización
        self.update_card_display()
        
        # Reiniciar estilos de botones
        for card_id, button in self.card_buttons.items():
            button.config(highlightbackground="#000000", highlightthickness=1)
        
        # Reiniciar etiquetas de resultados
        self.win_probability_label.config(text="Probabilidad de ganar: -")
        self.hand_strength_label.config(text="Fuerza de la mano: -")
        
        # Reiniciar sección de IA
        self.update_ai_advice_text("Los consejos de IA aparecerán aquí. Selecciona tus cartas para recibir análisis automático.\n\nIA: Hola, puedes preguntarme sobre estrategias de póker.")
        
        # Mensaje inicial
        self.show_status("Selecciona 2 cartas para tu mano")


# Función principal para iniciar la aplicación
def main():
    root = tk.Tk()
    app = TexasHoldemCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()