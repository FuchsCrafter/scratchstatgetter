from flask import Flask, render_template, request, redirect
import requests
import json

class projects:
    def __init__(self, id):
        self.id = id
    def getStats(self, stat):
        if stat == "loves" or stat == "faves" or stat == "views" or stat == "remixes":
            if stat == "loves":
                r = requests.get(
                    "https://api.scratch.mit.edu/projects/"+str(self.id))
                data = r.json()
                return data['stats']['loves']
            else:
                if stat == "faves":
                    r = requests.get(
                        "https://api.scratch.mit.edu/projects/"+str(self.id))
                    data = r.json()
                    return data['stats']['favorites']
                else:
                    if stat == "remixes":
                        r = requests.get(
                            "https://api.scratch.mit.edu/projects/"+str(self.id))
                        data = r.json()
                        return data['stats']['remixes']
                    else:
                        if stat == "views":
                            r = requests.get(
                                "https://api.scratch.mit.edu/projects/"+str(self.id))
                            data = r.json()
                            return data['stats']['views']
    
    def getComments(self):
        uname = requests.get(
            "https://api.scratch.mit.edu/projects/"+str(self.id)).json()
        if uname != {"code": "NotFound", "message": ""}:
            uname = uname['author']['username']
            data = requests.get("https://api.scratch.mit.edu/users/" +
                                str(uname)+"/projects/"+str(self.id)+"/comments").json()
            comments = []
            if data != {"code": "ResourceNotFound", "message": "/users/"+str(uname)+"/projects/175/comments does not exist"} and data != {"code": "NotFound", "message": ""}:
                x = ""
                for i in data:
                    if "content" in i:
                        x = i['content']
                    else:
                        if "image" in i:
                            x = i['image']
                        else:
                            x = "None"
                    comments.append(str('Username: '+str(uname))+(str(', Content: ')+str(x)))
                return data
    def getInfo(self):
        r = requests.get(
            'https://api.scratch.mit.edu/projects/'+str(self.id)
        ).json()
        return r
    def fetchAssets(self, type='img'):
        '''
        You may have problems with fetching assets since some projects may not have any assets, or are fetched as binary code and not JSON
        '''
        r = json.loads(requests.get(
            'https://projects.scratch.mit.edu/'+str(self.id)
        ).text.encode('utf-8'))
        
        assets = []
        for i in range(len(r['targets'])):
            if type == 'img':
                assets.append('https://cdn.assets.scratch.mit.edu/internalapi/asset/'+str(r['targets'][i]['costumes'][0]['md5ext'])+'/get')
            elif type == 'snd':
                assets.append('https://cdn.assets.scratch.mit.edu/internalapi/asset/'+str(r['targets'][i]['sounds'][0]['md5ext'])+'/get')
        return assets

class users:
    def __init__(self, user):
        self.user = user
        self.headers = {
            "x-csrftoken": "a",
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
            "referer": "https://scratch.mit.edu",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        }

    def exists(self):
        return requests.get("https://api.scratch.mit.edu/accounts/checkusername/"+str(self.user)).json() == {"username": self.user, "msg": "username exists"}
    
    def getMessagesCount(self):
        self.headers['referer'] = "https://scratch.mit.edu"
        return requests.get("https://api.scratch.mit.edu/users/"+str(self.user)+"/messages/count").json()['count']
    
    def getMessages(self):
        return requests.get("https://api.scratch.mit.edu/users/"+str(self.user)+"/messages" + "/", headers=self.headers).json()
    
    def getStatus(self):
        return requests.get("https://api.scratch.mit.edu/users/"+str(self.user)).json()['profile']['status']
    
    def getBio(self):
        return requests.get("https://api.scratch.mit.edu/users/"+str(self.user)).json()['profile']['bio']
    
    def getProjects(self):
        r = requests.get(
            "https://api.scratch.mit.edu/users/"+str(self.user)+"/projects")
        data = r.json()
        titles = []
        for i in data:
            x = i['title']
            y = i['id']
            titles.append('ID: ' + str(y))
            titles.append('Title: ' + str(x))
        return titles


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/kuchen')
def cakes():
    return 'Kuchen? Kuchen. Kuchen! KUCHEN!'

@app.route('/user/<username>')
def user(username):
    try:
        fetchedUser = users(username)
        messagecount = fetchedUser.getMessagesCount()
        bio = fetchedUser.getBio()
        status = fetchedUser.getStatus()
        userprojects = fetchedUser.getProjects()
        return render_template('user.html', username=username, messagecount=messagecount, bio=bio, status=status, userprojects=userprojects)
    except:
        return render_template('error_user.html', username=username)

@app.route('/existance/<username>')
def existance(username):
    try:
        fetchedUser = users(username)
        exists = fetchedUser.exists()
        if exists:
            return render_template('user_exists.html', username=username, userexists="")
        else:
            return render_template('user_exists.html', username=username, userexists="doesn't ")
    except:
        return render_template('error_user.html', username=username)



@app.route('/project/<projectid>')
def project(projectid):
    try: 
        fetchedProject = projects(projectid)
        views = fetchedProject.getStats("views")
        loves = fetchedProject.getStats("loves")
        faves = fetchedProject.getStats("faves")
        remixes = fetchedProject.getStats("remixes")
        return render_template("project.html", projectid=projectid, views=views, loves=loves, faves=faves, remixes=remixes)
    except:
        return render_template("error_project.html", projectid=projectid)

@app.route('/get')
def get():

  type =  request.args.get('type')
  id = request.args.get('id')
  try:
    return redirect("{}/{}".format(type, id), code=302)
  except:
    return render_template("get.html", type="type", id="id")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
