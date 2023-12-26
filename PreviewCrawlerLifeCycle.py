from database import dbinstance


data = "graph TD;\n"

cur = dbinstance.getCursor()

cur.execute("SELECT * FROM URLSTORE")

urlstore=cur.fetchall()
localurlstore=dict()

for row in urlstore:
    name=row[1].strip('https://uncutmaza.xyz')
    localurlstore[f"key_{row[0]}"]=name
    color = ""
    if row[2]:
        color=f"style {row[0]} fill:#FF0000;\n"
    else:
        color=f"style {row[0]} fill:#00FF00;\n"
    if not name:
        name="Start"
    
    data+=color+f"{row[0]}[{name}]\n"

data+="\n\n"
cur.execute("SELECT FROMURL,URL FROM CRAWLER_LIFECYCLE")

urlstore=cur.fetchall()
for row in urlstore:
    data+=f"{row[0]} --> {row[1]}\n"

with open("graph.md" , "w") as file:
    file.write(data)