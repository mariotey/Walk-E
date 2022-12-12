How to Kill VSCode remote services
1. Press ctrl + shift + p
2. Type " Remote-SSH: kill VS Code Server on Host..."
3. Select Host
4. Press enter 

How to Kill Flask server
1. Navigate to mctey@raspberrypi/
2. Type "bash terminateFlask.ssh"

How to Create Local Repository and push to Github
1. git init @ respository
2. git add .
3. git commit -m "Initial Commit"
4. git remote add origin <repository_url>
5. git push origin master
6. git push --set-upstream origin master

How to Clone Repository
1. git init @ repository
2. navigate to Profile -> Settings -> Developer settings -> Generate New Token
3. git clone https://<personal_access_token>@github.com/<github_account_username>/<github_repository>.git 
