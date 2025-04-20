# git add .
# git commit -m "$*"
# echo "committing with message \"$*\" "
# git push

Branch=$(git status | grep On | awk '{print $3}')
git add .
git commit -m "$*"
echo "--------------- committing with message \"$*\" "
git push -u origin $Branch
echo "---------------  Pushed to ===> $Branch"