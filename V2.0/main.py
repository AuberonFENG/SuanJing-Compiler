from app import create_app
import webbrowser

app = create_app()

    
if __name__ == "__main__":
    #this is to open the browser automatically
    webbrowser.open_new('http://127.0.0.1:8080/user/homepage')
    #run our application
    app.run(debug=True, host='127.0.0.1', port=8080)