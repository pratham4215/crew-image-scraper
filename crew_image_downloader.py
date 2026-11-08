import os
import re
import requests
from urllib.parse import urljoin, urlparse
import mimetypes
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq

# Load .env variables
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("MODEL", "groq/llama-3.1-8b-instant")
llm = ChatGroq(api_key=groq_api_key, model_name=model)

# Define Agent
scraper_agent = Agent(  
    role="Image Scraper",
    goal="Scrape and download all public images from a given webpage URL without using BeautifulSoup",
    backstory="You're a skilled scraper that works efficiently with raw HTML and regex to extract images.",
    verbose=True,
    llm=llm
)

# Download function without BeautifulSoup
def download_images_without_bs(url):
    print(f"[Agent] Scraping images from: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/122.0.0.0 Safari/537.36'
    }

    output_folder = "downloaded_images"
    os.makedirs(output_folder, exist_ok=True)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        html = response.text
        # Simple regex to find image sources
        image_urls = re.findall(r'<img[^>]+src="([^">]+)"', html)
        print(f"Found {len(image_urls)} image URLs")

        count = 0
        for img_src in image_urls:
            img_url = urljoin(url, img_src)
            try:
                img_response = requests.get(img_url, headers=headers)
                img_data = img_response.content

                parsed_url = urlparse(img_url)
                filename = os.path.basename(parsed_url.path)
                ext = os.path.splitext(filename)[1] or mimetypes.guess_extension(img_response.headers.get("Content-Type", "").split(";")[0]) or ".jpg"

                with open(os.path.join(output_folder, f"image_{count}{ext}"), "wb") as f:
                    f.write(img_data)

                print(f"Downloaded: {img_url}")
                count += 1
            except Exception as e:
                print("Error downloading:", img_url, "->", e)

        print(f"Downloaded {count} images to {output_folder}")
    else:
        print("Failed to fetch page. Status code:", response.status_code)

# Define Task
TARGET_URL = "https://all-free-download.com/free-photos/wallpaper-jpg.html"

scrape_task = Task(
    description=f"Extract and download all public images from {TARGET_URL} using regex and raw HTML only.",
    expected_output="A folder 'downloaded_images' with all images from the page.",
    agent=scraper_agent,
    async_execution=False,
    function=lambda: download_images_without_bs(TARGET_URL)
)

# Create Crew
crew = Crew(
    agents=[scraper_agent],
    tasks=[scrape_task],
    verbose=True
)

if __name__ == "__main__":
    crew.kickoff()
