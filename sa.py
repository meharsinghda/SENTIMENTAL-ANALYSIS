import streamlit as st
import requests
import google.generativeai as genai  # Import Google Generative AI (Gemini)
import os  # For handling environment variables

# Function to fetch news articles from NewsAPI
def fetch_news(api_key, query='technology'):
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={api_key}'
    response = requests.get(url)

    if response.status_code != 200:
        st.error("❌ Failed to fetch news. Please check your API key.")
        return []

    data = response.json()
    articles = data.get('articles', [])

    news_texts = [
        article['title'] + " - " + article['description']
        for article in articles if article.get('title') and article.get('description')
    ]

    return news_texts

# Function to get available models
def get_available_models(api_key):
    try:
        # Configure Gemini API with the provided API key
        genai.configure(api_key=api_key)
        
        # List all available models
        models = genai.list_models()  
        valid_models = [model.name for model in models if "generateContent" in model.supported_generation_methods and "vision" not in model.name.lower()]
        
        if valid_models:
            return valid_models
        else:
            st.error("No valid models found that support 'generateContent'.")
            return []
    except Exception as e:
        st.error(f"Error fetching models from Gemini: {e}")
        return []

# Function to analyze sentiment using Gemini (Google Generative AI)
def analyze_sentiment(texts, api_key, selected_model):
    # Set up Gemini API configuration with the API key
    genai.configure(api_key=api_key)
    
    sentiment_results = []

    try:
        prompt = "Analyze the sentiment (Positive, Neutral, Negative) of the following news articles:\n\n"
        prompt += "\n\n".join(texts[:5])  # Limit to 5 articles per request to optimize API usage

        # Create a generative model instance and request a response
        model = genai.GenerativeModel(selected_model)
        response = model.generate_content(prompt)

        # Split the response into individual sentiments
        sentiments = response.text.strip().split("\n")
        for text, sentiment in zip(texts[:5], sentiments):
            sentiment_results.append({'text': text, 'sentiment': sentiment})

    except Exception as e:
        st.error(f"⚠ Gemini API error: {e}")

    return sentiment_results

# Streamlit UI
def main():
    # Header Image
    st.image("https://via.placeholder.com/800x400.png?text=Sample+Image", use_column_width=True)

    st.title("📰 News Sentiment Analysis (Gemini)")

    # Input for news topic
    query = st.text_input("🔍 Enter a news topic:", "technology")

    # Input for API Keys
    newsapi_key = st.text_input("🔑 Enter your NewsAPI key:", type="password")
    genai_api_key = st.text_input("🔑 Enter your Google Gemini API key:", type="password")

    # Fetch available models for sentiment analysis
    if genai_api_key:
        available_models = get_available_models(genai_api_key)
    else:
        available_models = []

    if available_models:
        selected_model = st.selectbox("Choose a model for sentiment analysis", available_models)
    else:
        selected_model = None

    if st.button("🚀 Analyze Sentiment"):
        if newsapi_key and genai_api_key and selected_model:
            # Fetch news articles
            with st.spinner('🔄 Fetching news articles...'):
                news_data = fetch_news(newsapi_key, query)

            if news_data:
                # Perform sentiment analysis
                with st.spinner('🤖 Analyzing sentiment using Gemini...'):
                    sentiment_data = analyze_sentiment(news_data, genai_api_key, selected_model)

                # Display results
                st.subheader("📊 Sentiment Analysis Results:")
                for result in sentiment_data:
                    sentiment_color = "🟢" if "Positive" in result['sentiment'] else "🟡" if "Neutral" in result['sentiment'] else "🔴"
                    st.write(f"{sentiment_color} *{result['text']}*")
                    st.write(f"📝 *Sentiment:* {result['sentiment']}")
                    st.markdown("---")
            else:
                st.warning("⚠ No news articles found for the given topic.")
        else:
            st.warning("⚠ Please enter both API keys and select a valid model.")

if __name__ == "__main__":
    main()
