# AI-Trading Strategies: Quantum Brain V2 (BTC/USDT)

🚀 An automated quantitative trading system leveraging deep neural networks combined with statistical liquidity-hunting logic to predict price movements and execute optimal trades in the cryptocurrency market (BTC/USDT).

---

## 📂 Project Architecture

- **`main.py`**: The primary execution engine that manages the bot's lifecycle, signaling logic, and live simulation pipeline.
- **`brain_models.py`**: Contains the deep learning and neural network architectures (PyTorch) used for training and inference.
- **`data_ingestion.py`**: The data acquisition module responsible for fetching, cleaning, and preprocessing historical and real-time market data.
- **`database.py`**: Manages local data storage, transaction logging, and high-speed CSV/SQL caching to accelerate backtesting.
- **`dashboard.py`**: A graphical, interactive visualization interface to monitor real-time portfolio value, equity curves, and active trade metrics.
- **`quantum_brain_v2_btc.pt`**: The core trained neural network weights file, pre-compiled and ready for deployment.

---

## 🧠 Neural Network & Strategic Model

The first iteration model, `quantum_brain_v2_btc`, is built upon a deep feedforward network specifically optimized to extract structural signals out of highly volatile 15-minute intervals:

1. **Input Layer**: Ingests multiple calculated dimensions including Volume-Weighted Momentum, Volatility Adjusted Z-Scores, and localized RSI proxies.
2. **Hidden Layer Topography**: Features dense fully connected layers heavily integrated with Regularization components (**Dropout** and **Batch Normalization**) to actively mitigate overfitting caused by short-term market noise.
3. **Risk Management Module**: Neural predictions are fed straight into an algorithmic execution guard. Stops and targets are calculated dynamically utilizing Average True Range (ATR) multipliers, accompanied by a custom **Trailing Break-Even Protection Engine** to lock in profits early.

---

## 🛠️ Installation & Quick Start

### 1. Prerequisite Installations

Ensure your Python environment is equipped with the core data science and deep learning frameworks:

```bash
pip install torch pandas numpy matplotlib binance-python flask
```
