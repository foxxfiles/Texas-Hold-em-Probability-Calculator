
# Texas Hold'em Probability Calculator

This application is a sophisticated tool designed to calculate winning probabilities for Texas Hold'em poker. By analyzing your hole cards, community cards, and the number of opponents, it computes your chance of winning the current hand. Additionally, it leverages AI models to provide strategic advice and includes a chat interface to interact with an AI assistant for further insights. This solves the problem faced by poker players who need accurate, real-time odds and guidance to make informed decisions at the table.

## Quick start

Follow these instructions to start the project from scratch on Linux, macOS, or Windows:

### Clone the repository

```bash
git clone https://github.com/foxxfiles/texas-holdem-calculator.git
cd texas-holdem-calculator
```

### Linux / macOS

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install project dependencies
pip install -r requirements.txt

# 3. Run the application
python3 ppoker.py
```

### Windows (CMD)

```cmd
:: 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

:: 2. Install project dependencies
pip install -r requirements.txt

:: 3. Run the application
python ppoker.py
```

### Dependencies

- Python 3.7 or higher
- `requests`
- `openai`

All dependencies are listed in `requirements.txt`. Install them using the commands above.

## config.json (optional)

If you want to enable AI-driven recommendations and chat features, create a `config.json` file in the root directory. Below is an example of the fundamental and optional fields:

```json
{
  "api": {
    "openai_model_1": {
      "api_type": "openai",
      "api_key": "YOUR_OPENAI_API_KEY",
      "api_base_url": "https://api.openai.com/v1",
      "model": "gpt-3.5-turbo",
      "weight": 1.0
    }
  }
}
```

- **api**: Top-level key grouping multiple AI model configurations.
- **openai_model_1**: Identifier for a specific AI configuration (you can name this entry arbitrarily).
  - **api_type** (string, required): Must be `"openai"` for OpenAI models.
  - **api_key** (string, required): Your OpenAI API key.
  - **api_base_url** (string, required): The base URL for the OpenAI API (e.g., `https://api.openai.com/v1`).
  - **model** (string, required): Model identifier (e.g., `"gpt-3.5-turbo"`).
  - **weight** (float, optional): Relative weight used when combining multiple model responses (default: `1.0`).

You can add multiple AI configurations under the `api` object. If no `config.json` is provided, AI features will be disabled, and manual advice requests will not work.

## Usage guide

### Launch the application

1. Ensure that all dependencies are installed (see **Quick start**).
2. Run the application with `python ppoker.py` (or `python3 ppoker.py`).
3. A GUI window will open, displaying slots for community cards, your hand, and a mini-deck for card selection.

### Select your hole cards

1. In the “SELECCIONA TUS CARTAS” section, click on any two cards from the mini-deck.
2. The selected cards will appear in the “TU MANO” section.
3. Once two cards are selected, preliminary odds will be calculated automatically.

### Select community cards

1. Click on any five cards from the mini-deck to represent the community cards.
2. The chosen cards will appear under “CARTAS COMUNITARIAS”.
3. If fewer than five community cards are selected, the remaining slots will display a placeholder.
4. After all five community cards are chosen, click **CALCULAR** to update the final winning probability.

### Configure number of opponents

1. In the “Oponentes” field at the bottom-left, set the number of opponents (1–9).
2. The number of opponents influences the Monte Carlo simulation for odds calculation.
3. Changing this value will automatically update AI advice (if configured).

### Calculate probabilities

1. After selecting two hole cards and up to five community cards, click the **CALCULAR** button.
2. The application performs a Monte Carlo simulation (1,000 iterations) to estimate winning probability.
3. The labels “Probabilidad de ganar” and “Fuerza de la mano” will update with results in Spanish.
4. Strategic recommendations based on the computed probability will appear in the status message.

### Interpret hand strength

- **Royal Flush**: Highest possible hand; extremely rare.
- **Straight Flush**: Five consecutive cards of the same suit.
- **Four of a Kind**: Four cards of identical rank.
- **Full House**: Three of a kind combined with a pair.
- **Flush**: Five cards of the same suit (not consecutive).
- **Straight**: Five consecutive cards (mixed suits).
- **Three of a Kind**: Three cards of the same rank.
- **Two Pair**: Two different pairs.
- **Pair**: Two cards of the same rank.
- **High Card**: None of the above; highest single card.

### View AI-driven advice

1. If `config.json` is present and valid, AI advice is fetched automatically whenever you select two hole cards.
2. The AI will display:
   - Evaluation of your current hand.
   - Odds of improving (if community cards are present).
   - Specific strategic recommendation.
3. To manually request AI advice, click the **CONSEJO AI** button (visible only if no automatic AI configuration was detected).
4. Type your question in the “CHAT CON LA IA” field and press **Preguntar** or Enter to get contextual responses.

### Reset the application

1. Click the **REINICIAR** button to clear all selected cards, probabilities, and AI advice.
2. The UI will return to its initial state, prompting you to select two hole cards.

---

YouTube channel: https://www.youtube.com/@efoxxfiles
