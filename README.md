ToxHub Cooking
=====

**Sharing ToxHub python code**

### What is this?

In this repository members of eTransafe can share python scripts written that do fun things in ToxHub

for example:

- Compare psur and faers data
- Display most frequent findings for compound by case count from ct.gov
- Use the ToxHub lib with a locally running primitive adaptor
- Show the classic omeprazole heatmaps

### Requirements:

The latest version of the python ToxHub lib

```bash
pip install -i https://test.pypi.org/simple/ toxhub --upgrade
````

### How to use

Copy the `credentials_example.py` file, and rename one of them to `credentials.py`  store your ToxHub credentials there.

You should now be able to run any of the files in the `recipes` folder

Put scrips you don't want to share in the `secretrecipes` folder, they will not be committed to git.
Things you would like to share can go in the `recipes` folder, handy reusable pieces can be placed in the `supermarket`

Pictures, charts and files that are generated are saved in the `output` folder

### Contributions

Contributions and constructive feedback are welcome, open a pull request

