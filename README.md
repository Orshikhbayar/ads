# Amazon Ads Automation Platform

A powerful automation platform for Amazon advertising campaigns, built with AI-powered segment generation and keyword optimization.

## 🚀 Features

- **AI-Powered Campaign Generation**: Automatically generate targeted advertising segments based on campaign briefs
- **Smart Keyword Translation**: Seamless English-to-Japanese keyword translation for international campaigns  
- **Intelligent Segment Retrieval**: Find the most relevant audience segments using advanced matching algorithms
- **Real-time Campaign Optimization**: Dynamic adjustment of targeting parameters and bid strategies
- **Interactive Web Interface**: User-friendly dashboard for campaign management and monitoring

## 🛠️ Built With

- **Backend**: Python Flask with OpenAI integration
- **Frontend**: Modern web interface with real-time updates
- **AI/ML**: OpenAI GPT models for content generation and translation
- **Data Processing**: Advanced embedding models for semantic matching

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Required environment variables (see setup section)

## ⚙️ Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   EMBEDDING_BACKEND=your_embedding_backend
   EMBEDDING_MODEL=your_embedding_model
   ```
4. Run the application: `python app.py`

## 🎯 Usage

The platform provides both API endpoints and a web interface for:
- Generating campaign segments from briefs
- Retrieving similar segments from existing data
- Translating keywords for international markets
- Optimizing campaign performance

## 📊 API Endpoints

- `POST /api/generate` - Generate new campaign segments
- `POST /api/retrieve` - Retrieve similar segments
- `GET /health` - Health check endpoint

## 🤝 Contributing

This project is actively developed and maintained. Feel free to submit issues and enhancement requests.

## 📄 License

This project is licensed under the MIT License.

---

*Built with ❤️ for Amazon advertising automation*
