from bs4 import BeautifulSoup
import pandas as pd

# Read the HTML file
with open('rankingUniversities.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table with the class 'sticky-enabled'
table = soup.find('table', {'class': 'sticky-enabled'})

# Check if the table was found
if table is None:
    raise ValueError("Table with class 'sticky-enabled' not found in the HTML.")

# Extract table headers
thead = table.find('thead')
headers = []
if thead:
    headers = [th.get_text(strip=True) for th in thead.find_all('th')]
else:
    raise ValueError("No 'thead' section found in the table.")

# Extract table rows
rows = []
tbody = table.find('tbody')
if tbody:
    for row in tbody.find_all('tr'):
        cells = row.find_all('td')
        # Extract text from cells and remove extra spaces
        row_data = [cell.get_text(strip=True) for cell in cells]
        rows.append(row_data)
else:
    raise ValueError("No 'tbody' section found in the table.")

# Convert to DataFrame
df = pd.DataFrame(rows, columns=headers)

# Display the DataFrame
print(df)

# Optionally, save to CSV
df.to_csv('university_rankings.csv', index=False)
