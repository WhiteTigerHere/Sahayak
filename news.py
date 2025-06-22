from gtts import gTTS
import os
from cohere_chat import init_client, fetch_response
import requests
from bs4 import BeautifulSoup

# Initialize Cohere client
co = init_client()

def speak(text, language="en"):
    """Convert text to speech and play it."""
    tts = gTTS(text=text, lang=language)
    tts.save("output.mp3")
    os.system("start output.mp3")

def news_scrape():
    """Scrapes news from India Today and returns a list of news articles with title, link, and image."""
    base_url = "https://www.indiatoday.in"
    url = "https://www.indiatoday.in/india"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_data = []
        articles = soup.find_all('div', class_='B1S3_content__thumbnail__wrap__iPgcS')

        for article in articles:
            try:
                # Extract link
                link_tag = article.find('a', href=True)
                link = f"{base_url}{link_tag['href']}" if link_tag and link_tag['href'].startswith('/') else link_tag['href']

                # Extract title
                title = link_tag['title'] if 'title' in link_tag.attrs else "No Title"

                # Extract image link
                image_tag = article.find('img')
                image_link = image_tag['src'] if image_tag and 'src' in image_tag.attrs else "No Image"

                # Append the news article
                news_data.append({
                    'title': title,
                    'link': link,
                    'image_link': image_link
                })
            except Exception as e:
                print(f"Error processing article: {e}")
        return news_data
    else:
        print(f"Failed to fetch news. Status code: {response.status_code}")
        return []

def news_personalized():
    """Provides personalized news recommendations based on user input and scraped data."""
    # Step 1: Prompt user with TTS
    speak("What type of news would you like? Please type your preference.", "en")
    print("What type of news would you like? Please type your preference below:")
    news_type = input("Your preference: ")
    if not news_type:
        speak("I couldn't understand your preference. Please try again.", "en")
        print("Could not capture your preference. Please try again.")
        return

    # Step 2: Scrape news
    news_data = news_scrape()
    if not news_data:
        speak("Sorry, I couldn't fetch news at this time.", "en")
        print("No news data available. Exiting.")
        return

    for n in news_data:
        print(f"Title: {n['title']}")
        print(f"Link: {n['link']}")
        print("*" * 50)
    # Step 3: Prepare Cohere input
    titles = [news['title'] for news in news_data]
    prompt = f"Find news articles related to '{news_type}'. Here are some titles:\n" + "\n".join(titles)

    # Step 4: Fetch personalized recommendations from Cohere
    messages = [{"role": "user", "content": prompt}]
    personalized_response = fetch_response(co, messages)

    # Step 5: Filter relevant news
    recommendations = personalized_response.split("\n")
    filtered_news = [news for news in news_data if any(rec in news['title'] for rec in recommendations)]
    # filtered_news = filtered_news[:100]

    # Step 6: Display results
    speak("Here are your personalized news recommendations.", "en")
    print("\nPersonalized News Recommendations:")
    for news in filtered_news:
        print(f"Title: {news['title']}")
        print(f"Link: {news['link']}")
        print(f"Image: {news['image_link']}")
        print("-" * 50)

def news_personalized1(news_type):
    """Provides personalized news recommendations based on user input and scraped data."""
    # Step 1: Prompt user with TTS

    if not news_type:
        speak("I couldn't understand your preference. Please try again.", "en")
        print("Could not capture your preference. Please try again.")
        return

    # Step 2: Scrape news
    news_data = news_scrape()
    if not news_data:

        return None

    titles = [news['title'] for news in news_data]
    prompt = f"Find news articles related to '{news_type}'. Here are some titles:\n" + "\n".join(titles)

    # Step 4: Fetch personalized recommendations from Cohere
    messages = [{"role": "user", "content": prompt}]
    personalized_response = fetch_response(co, messages)

    # Step 5: Filter relevant news
    recommendations = personalized_response.split("\n")
    filtered_news = [news for news in news_data if any(rec in news['title'] for rec in recommendations)]
    # filtered_news = filtered_news[:100]

    for news in filtered_news:
        print(f"Title: {news['title']}")
        print(f"Link: {news['link']}")
        print(f"Image: {news['image_link']}")

    return filtered_news

if __name__ == "__main__":
    news_personalized1("crime")