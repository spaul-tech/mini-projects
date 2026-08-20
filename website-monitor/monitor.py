import requests as req
import pandas as pd
from urllib.parse import urlparse

link=["https://google.com",
      "https://github.com",
      "https://amazon.com",
      "https://facebook.com"]

results=[]
for i in link:
    r=req.get(i)
    d={
        "url": urlparse(i).netloc,
        "status_code": r.status_code,
        "content_type": r.headers['Content-Type'],
        "Server": r.headers.get("Server", "Unknown"),
        "Response_time": r.elapsed.total_seconds()
    }
    results.append(d)

df=pd.DataFrame(results)
df.to_csv("report.csv", index=False)  #this automatically saves the output in the file
