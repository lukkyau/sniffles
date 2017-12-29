Create test and train/learn datasets
random_indices = permutation(df.index)
test_cutoff = math.floor(len(df)/3)
test = df.loc[random_indices[1:test_cutoff]]
train = df.loc[random_indices[test_cutoff:]]

# Use scikit-learn to predict
from sklearn.neighbors import KNeighborsClassifier
x_columns=['AP1','AP2','AP3','AP4']
y_column=['location']
knn=KNeighborsClassifier(n_neighbors=3)
knn.fit(train[x_columns],train[y_column].values.ravel())
predictions = knn.predict(test[x_columns])

# Check error rate
actual = test[y_column]
actual['predicted']=predictions
actual