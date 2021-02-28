from setuptools import setup, find_packages

# Setting up
setup(
        name="boards", 
        version="0.0.1",
        author="Ben Newhouse",
        author_email="<newhouseb@gmail.com>",
        description="assorted nmigen boards",
        packages=find_packages(),
        install_requires=[
		"nmigen>=0.2,<0.4",
                "nmigen-boards",
	], # add any additional packages that 
        keywords=['python', 'nmigen'],
        classifiers= []
)
