import numpy as np
from sklearn.linear_model import LinearRegression

X = np.array([-1, 1, 2, 3, 4]).reshape(-1, 1)
y = [6.41, -0.79, -4.39, -7.99, -11.59]

model = LinearRegression()
model.fit(X, y)
print(model.intercept_, model.coef_)
