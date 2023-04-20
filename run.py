import sys
sys.path.append(r'C:\Users\tareks\OneDrive - Earnix\Desktop\Personal\Online-Inventory-Management-Software-master\Online-Inventory-Management-Software-master')
# from orders import app
from orders import app, db


# app = create_app()



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
    # app.run()  # ngrok




