# Code Reviewer (WEB)

A codereviewer for fortran code analyses rule compliances.

```
fortran-rule-checker-webapp
├── src
│   ├── app.py               # Main entry point 
│   ├── static
│   │   └── styles.css       # CSS styles  
│   ├── templates
│   │   └── index.html       # Main HTML template
├── requirements.txt         # Project dependencies
└── README.md                # Documentation for the project
```


## VirtuaL Enviroment
```bash
 $ python3 -m venv VenvPythonWeb
 $ source VenvPythonWeb/bin/activate
```

## Running in terminal

```bash
   $python3 app.py
```

## Installing requirements: 

  - fparser
```bash
   $pip install fparser
```
  - flask
```bash
   $pip install flask
```

### requirements web server to flask

```bash
   $pip install gunicorn
```

```bash
   $sudo apt update
   $sudo apt install nginx
```



