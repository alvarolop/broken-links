import requests
import sys
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
from datetime import datetime
import webbrowser

searched_links = []
broken_links = []

TODAY = datetime.today().strftime('%Y-%m-%d')
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://pratapsharma.io"
WEBSITE  = urlparse(BASE_URL).netloc.replace('.', '-')

FILE_PATH = f"reports/{WEBSITE}-{TODAY}-broken-links.html"

print(f'Running script for {BASE_URL} and saving the file to: {FILE_PATH}')


def getLinksFromHTML(html):
    def getLink(el):
        return el["href"]
    return list(map(getLink, BeautifulSoup(html, features="html.parser").select("a[href]")))


def find_broken_links(domainToSearch, URL, parentURL, counter = 0):
    is_searchable = (not (URL in searched_links)) and (not URL.startswith("mailto:")) and (not ("javascript:" in URL)) and (
        not URL.endswith(".png")) and (not URL.endswith(".jpg")) and (not URL.endswith(".jpeg"))
    if is_searchable:
        try:
            resetObj = requests.get(URL)
            searched_links.append(URL)
            print('\r', "Links analyzed: " + str(counter), end = '')
            if(resetObj.status_code == 404):
                broken_links.append({
                    "url": URL,
                    "parent_url": parentURL or 'Home',
                    'message': resetObj.reason
                })
                print("Error analyzed: " + str(resetObj.status_code))
            else:
                if urlparse(URL).netloc == domainToSearch:
                    for link in getLinksFromHTML(resetObj.text):
                        find_broken_links(
                            domainToSearch, urljoin(URL, link), URL, counter+1)
        except Exception as e:
            print("ERROR: " + str(e))
            searched_links.append(domainToSearch)


find_broken_links(urlparse(BASE_URL).netloc, BASE_URL, "", )

# Converting above errors to html file
with open(f'{FILE_PATH}', 'w') as myFile:
    myFile.write('<html>')
    myFile.write(f'''
        <head>
            <style>
            table {{
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
            }}

            td, th {{
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }}

            tr:nth-child(even) {{
                background-color: #dddddd;
            }}
            h2 {{
                text-align: center;
            }}
            </style>
        </head>
    ''')
    myFile.write('<body>' + '\n')
    myFile.write(f'<h2>Broken links for site: {BASE_URL}</h2>' + '\n')
    myFile.write('<table>' + '\n')
    myFile.write('<tbody>' + '\n')
    myFile.write('''
        <tr>
            <th>SN</th>
            <th>URL</th>
            <th>Parent URL</th>
            <th>Message</th>
        </tr>
    ''')

    for index, link in enumerate(broken_links):
        myFile.write('''
        <tr>
            <td>{0}</td>
            <td><a href="{1}" style="color:red;" target="_blank">{1}</a></td>
            <td><a href="{2}" target="_blank">{2}</a></td>
            <td>{3}</td>
        </tr>
        '''.format(index+1, link['url'], link['parent_url'], link['message']))
    myFile.write('</tbody>'+ '\n')
    myFile.write('</table>'+ '\n')
    myFile.write('</body>'+ '\n')
    myFile.write('</html>'+ '\n')

# Selecting chrome as a browser and opening th html file in the browser
# browser = webbrowser.get('google-chrome')
webbrowser.open_new_tab(f'file://{FILE_PATH}')
