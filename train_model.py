import pickle
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from collections import Counter
from sklearn.utils import shuffle

# LOAD DATA
with open("data.pkl", "rb") as f:
    data, labels = pickle.load(f)

# kiểm tra phân bố dữ liệu
print("Label distribution:", Counter(labels))

# shuffle
data, labels = shuffle(data, labels)
# load data
with open("data.pkl", "rb") as f:
    data, labels = pickle.load(f)

X_train, X_test, y_train, y_test = train_test_split(
    data, labels, test_size=0.2
)

model = RandomForestClassifier()
model.fit(X_train, y_train)

print("Accuracy:", model.score(X_test, y_test))

# save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

