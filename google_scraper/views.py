
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.shortcuts import render
import logging
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

@csrf_exempt
def scrape_and_process(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        location = request.GET.get('location')
        max_results = int(request.GET.get('max_results', 5))

        if not query or not location:
            return JsonResponse({'error': 'Query and location are required.'}, status=400)

        try:
            business_data = scrape_google_maps(query, location, max_results)
            if business_data:
                result = process_business_data(business_data)
                return JsonResponse({'result': result})
            else:
                return JsonResponse({'error': 'No data found.'}, status=500)
        except Exception as e:
            logger.exception("Scraping failed")
            return JsonResponse({'error': f'Scraping failed: {e}'}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

def scrape_google_maps(query, location, max_results=5):
    """Scrape business data from Google Maps using Selenium."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-features=UseSkiaRenderer")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    try:
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.google.com/maps")
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
            search_box = driver.find_element(By.ID, "searchboxinput")
            search_box.send_keys(f"{query} in {location}")
            search_box.send_keys(Keys.RETURN)

            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))
            scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')

            for _ in range(5):
                driver.execute_script("arguments[0].scrollTop += 1000;", scrollable_div)
                time.sleep(2)

            businesses = []
            results = driver.find_elements(By.XPATH, '//div[contains(@aria-label, "Results for")]//div[@role="article"]')

            for result in results[:max_results]:
                try:
                    name = WebDriverWait(result, 10).until(EC.presence_of_element_located((By.XPATH, './/div[contains(@aria-label, "Rating")]/preceding-sibling::div'))).text
                    address = WebDriverWait(result, 10).until(EC.presence_of_element_located((By.XPATH, './/span[contains(text(), "Address")]/following-sibling::span'))).text
                    rating_elem = result.find_elements(By.XPATH, './/span[contains(@aria-label, "stars")]')
                    rating = rating_elem[0].get_attribute("aria-label") if rating_elem else "N/A"
                    phone_elem = result.find_elements(By.XPATH, './/button[contains(@aria-label, "Phone")]')
                    phone = phone_elem[0].get_attribute("aria-label") if phone_elem else "N/A"
                    website_elem = result.find_elements(By.XPATH, './/a[contains(@href, "http")]')
                    website = website_elem[0].get_attribute("href") if website_elem else "N/A"

                    businesses.append({
                        "name": name,
                        "address": address,
                        "rating": rating,
                        "phone": phone,
                        "website": website,
                    })

                except (TimeoutException, NoSuchElementException) as e:
                    logger.warning(f"Error extracting data: {e}")
                    continue

            return businesses

        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Selenium error: {e}")
            return []

    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        return []

    finally:
        if 'driver' in locals():
            driver.quit()

def interact_with_llm(prompt):
    """Interacts with Vertex AI."""
    llm_api_url = os.environ.get("VERTEX_AI_ENDPOINT")
    api_key = os.environ.get("GOOGLE_CLOUD_API_KEY")

    if not api_key or not llm_api_url:
        logger.error("API key or endpoint not found in environment variables.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "temperature": 0.2,
            "maxOutputTokens": 256,
        },
    }

    try:
        response = requests.post(llm_api_url, headers=headers, json=data)
        response.raise_for_status()
        llm_response = response.json()["predictions"][0]["content"]
        return llm_response
    except requests.exceptions.RequestException as e:
        logger.exception(f"Error interacting with Vertex AI: {e}")
        return None
    except KeyError:
        logger.error("Vertex AI response did not include expected keys.")
        return None

def process_business_data(businesses):
    """Processes scraped business data using an LLM."""
    if not businesses:
        return "No business data to process."

    ratings = [business["rating"] for business in businesses if business["rating"] != "N/A"]
    if not ratings:
        return "No ratings found."

    prompt = f"Here are the ratings: {ratings}. What is the average rating? Provide only the number."
    llm_response = interact_with_llm(prompt)

    if llm_response:
        return f"Average rating: {llm_response}"
    else:
        return "Could not calculate average rating."

def scraper_page(request):
    return render(request, 'scrape_form.html')