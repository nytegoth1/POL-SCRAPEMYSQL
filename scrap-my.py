import requests
from bs4 import BeautifulSoup
import mysql.connector

def scrape_site(url):
    # Send a GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all li elements with the class name 'o-listicle__item'
    sections = soup.find_all('li', class_='o-listicle__item')

    # Extract information from each section
    data = []
    for section in sections:
        section_info = {}
        # Extract text content
        section_info['text'] = section.get_text(strip=True)
        # Extract img src if present
        img = section.find('img')
        if img and img.get('src'):
            section_info['img_src'] = img['src']
        data.append(section_info)

    return data

def save_to_mysql(data):
    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",       # Change to your MySQL server's address
        user="root",            # Change to your MySQL username
        password="",    # Change to your MySQL password
        database="pyscrape"  # Make sure the database exists
    )
    
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        text TEXT NOT NULL,
        img_src VARCHAR(255)
    )
    """)

    # Insert each record into the table
    for section in data:
        cursor.execute("""
        INSERT INTO scraped_data (text, img_src) 
        VALUES (%s, %s)
        """, (section['text'], section.get('img_src')))
    
    # Commit the transaction
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()
    print("Data has been saved to MySQL")

if __name__ == '__main__':
    url = 'https://www.politifact.com/personalities/donald-trump'  # Replace with the URL you want to scrape
    scraped_data = scrape_site(url)
    save_to_mysql(scraped_data)
