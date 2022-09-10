from website import create_app

app = create_app()

if __name__ == '__main__':
     app.run(debug=True)
     #  - add access for other PC in local network on host IP addr