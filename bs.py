from bs4 import BeautifulSoup

h = """
<html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <p>Hello, World!</p>
    </body>
</html>
"""

soup = BeautifulSoup(h, 'html.parser')
print(soup.html.body.text)
