from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import mimetypes

load_dotenv()
groq_api_key= os.getenv("GROQ_API_KEY")
model= os.getenv("MODEL", "groq/llama-3.1-8b-instant")
llm= ChatGroq(api_key=groq_api_key, model= model, temperature= 0)

"""llm= LLM(
    model="openrouter/deepseek/deepseek-r1",
    base_url="https://openrouter.ai/api/v1",
    api_key= os.getenv("OPENROUTER_API_KEY")
)"""

#Agent to parse the internet.
@tool
def download_images(url, topic):
    """This tool takes the website url and topic to be searched. It outputs, the images found in the url into a folder with name: "topic" """
    print(f"Scraping images from: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/122.0.0.0 Safari/537.36'
    }

    # Create output folder
    output_folder = f"downloaded_images/{topic}"
    os.makedirs(output_folder, exist_ok=True)

    response = requests.get(url, headers=headers)
    
    

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img')
        print(f"Found {len(images)} image tags.")
        count = 0

        for image in images:
            image_url = image.get('src') or image.get('data-src')

            if image_url:
                # Convert relative URLs to full URLs
                image_url = urljoin(url, image_url)

                if image_url.startswith('http'):
                    print("Downloading image:", image_url)
                    try:
                        img_response = requests.get(image_url, headers=headers)
                        img_data = img_response.content

                        # Guess file extension
                        parsed_url = urlparse(image_url)
                        filename = os.path.basename(parsed_url.path)
                        ext = os.path.splitext(filename)[1]
                        if not ext:
                            ext = mimetypes.guess_extension(img_response.headers.get("Content-Type", "").split(";")[0])
                        if not ext:
                            ext = ".jpg"  # default fallback

                        # Save image
                        with open(os.path.join(output_folder, f"image_{count}{ext}"), "wb") as f:
                            f.write(img_data)
                        count += 1
                    except Exception as e:
                        print("Failed to download:", image_url, "| Error:", e)
                else:
                    print("Skipping invalid URL:", image_url)
            else:
                print("No src or data-src found for image tag.")

        print(f"Downloaded {count} images.")
        print(f"Images saved to: {os.path.abspath(output_folder)}")
    else:
        print("Failed to retrieve webpage. Status code:", response.status_code)

"""image_downloader_tool = Tool(
    name="DownloadImages",
    func=image_scraper,
    description="Downloads all images from a given URL and saves them locally."
)"""


#Agent to parse the internet.
parser_agent= Agent(
    role= "Searches and finds top 5 websites for {topic}.",
    goal= "To Provide website links with dedicated images for {topic}",
    backstory= "Built to search for websites with related images to {topic}.",
    respect_context_window= True,
    llm=llm,    
    verbose= True    
)

image_downloader= Agent(
    role= "Finds and download images from given websites links.",
    goal= "To downlad top images related to {topic} from given links with only '.jpg','.svg','.png','.jpeg' extensions",
    backstory= "Designed to support dataset building and visual asset collection across domains.",
    respect_context_window= True,
    allow_code_execution= True,
    #tools=[download_images],
    llm= llm,
    verbose= True    
)


parse_task= Task(
    description= "Search the internet for URLs of a given {topic}",
    expected_output="A Python list of valid website links related to the {topic}, e.g., ['https://example1.com', 'https://example2.com']",
    agent= parser_agent,
    name= "web_parser"    
)

downloader_task= Task(
    description="Parse the provided websites, find 5 image files with only '.jpg','.svg','.png','.jpeg' extensions and download them. ",
    expected_output="A local directory with all the images downloadad to a predefined location", 
    agent= image_downloader,
    context= [parse_task],
    name= "Image downloader"
)


crew= Crew(
    agents=[parser_agent, image_downloader],
    tasks=[parse_task, downloader_task],
    process= Process.sequential,
    verbose= True
)

crew_output= crew.kickoff(inputs={"topic": "porsche 911"})

print(f"Raw Output: {crew_output.raw}")
#print(f"Tasks Output: {crew_output.tasks_output}")
#print(f"Token Usage: {crew_output.token_usage}")