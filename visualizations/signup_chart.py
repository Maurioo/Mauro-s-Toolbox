import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/active_customers.csv")
df['signup_year'].value_counts().sort_index().plot(kind='bar')
plt.title("Aantal actieve klanten per jaar")
plt.xlabel("Jaar")
plt.ylabel("Aantal klanten")
plt.show()
