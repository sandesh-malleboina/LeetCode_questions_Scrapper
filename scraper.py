from playwright.sync_api import sync_playwright
import time
from datetime import datetime, timedelta
import json


cutoff_date = datetime(2025, 1, 1)#################################################

company_keywords = [
    "Adobe",
    "High Radius",
    "Uplers",
    "Optym",
    "Cars 24",
    "ByteDance",
    "WyreFlow",
    "Citadel Securities",
    "Delta Airlines",
    "Intuit",
    "Apple",
    "JPMorgan Chase",
    "jpmc",
    "Microsoft",
    "Morgan Stanley",
    "NK Sequrities",
    "NVIDIA",
    "Openmesh Networks",
    "Optiver",
    "Palantir",
    "Applied Materials",
    "PayPal",
    "Qualcomm",
    "Salesforce",
    "ServiceNow",
    "Slice",
    "Square",
    "TikTok",
    "Twilio",
    "Visa",
    "Warner Bros Discovery",
    "Texas Instruments",
    "Uber",
    "Google",
    "Ebullient Securities",
    "Quadeye",
    "American Express",
    "JPMC",
    "Goldman Sachs",
    "DE Shaw",
    "Wells Forgo"
]


content_keywords = ["reject", "accept","experience","round", "question"]##################################################
valid_posts = 0
max_posts = 20000 ##################################


def convert_to_timestamp(text):
    now = datetime.now()
    if "minute" in text:
        n = int(text.split()[0])
        return now - timedelta(minutes=n)
    elif "hour" in text:
        n = int(text.split()[0]) if text[0].isdigit() else 1
        return now - timedelta(hours=n)
    elif "day" in text:
        return now - timedelta(hours=24)
    else:
        return datetime.strptime(text, "%b %d, %Y")  



def contains_company(title):
    return any(company.lower() in title.lower() for company in company_keywords)

def contains_keywords(text):
    text = text.lower()
    return any(
        word in text or word + 's' in text or word + 'es' in text or word + 'ed' in text 
        for word in content_keywords
    )


with sync_playwright() as p:
    start = time.time()
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()  # Assumes you're logged in and saved auth
    page = context.new_page()

    page.goto("https://leetcode.com/discuss/interview-experience", timeout=60000)
    
    interview_button = page.locator("button >> span:text-is('Interview')")
    interview_button.first.click()

    page.wait_for_selector("button:has-text('Newest')").click()
    page.wait_for_timeout(2000)

    post_links = set()
    
    print("Starting...")
    time.sleep(3)  ##################################################
    
    cons=0
    
    while valid_posts < max_posts:
        links = page.query_selector_all("a.no-underline.truncate.flex")
        for link in links:
            href = link.get_attribute("href")
            title_div = link.query_selector("div.text-sd-foreground")
            text = title_div.inner_text() if title_div else "No title"
            if href and contains_company(text) and href not in post_links:
                post_links.add(href)
                new_tab = context.new_page()
                new_tab.goto(f"https://leetcode.com{href}")
                new_tab.wait_for_selector("div.mYe_l.TAIHK", timeout=10000)

                date = new_tab.locator('span[data-state="closed"]').first.inner_text()
                date=convert_to_timestamp(date)

                if date>cutoff_date:
                    cons=0
                    content = new_tab.locator("div.mYe_l.TAIHK").inner_text()
                    if contains_keywords(content):
                        print("Scraped: ",text)
                        valid_posts+=1
                        with open("scraped_posts.ndjson", "a", encoding="utf-8") as f:
                            f.write(json.dumps({
                                "title": text,
                                "url": f"https://leetcode.com{href}",
                                "date": date.strftime("%Y-%m-%d %H:%M:%S"),  # ✅ Convert to string
                                "content": content[:5000]
                            }))
                            f.write("\n")

                        
                else:
                    cons+=1
                new_tab.close()

                if valid_posts >= max_posts:
                    break
        if cons>10:
            print("no more posts")
            break
        page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)

    end = time.time()
    print(f"\nScraped {valid_posts} posts in {end - start:.2f} seconds.")

    browser.close()
