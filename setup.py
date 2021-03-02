import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DocOnce",
    version="1.5.6",
    author='Hans Petter Langtangen, Alessandro Marin',
    author_email="hpl@simula.no, Alessandro.Marin@fys.uio.no",
    maintainer = "Kristian Gregorius Hustad",
    maintainer_email = "krihus@ifi.uio.no",
    description="Markup language similar to Markdown targeting scientific reports, software documentation, books, blog posts, and slides. DocOnce can generate LaTeX, Sphinx, HTML, IPython notebooks, Markdown, MediaWiki, and other formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license = "BSD",
    url="https://github.com/doconce/doconce",
    project_urls={
        "Issues on GitHub": "https://github.com/doconce/doconce/issues",
    },
    packages = ['doconce'],
    package_dir = {'': 'lib'},
    python_requires=">=3.6",
    scripts = ['bin/doconce'],
    install_requires=[
        'pygments',
        'preprocess',
        'wheel',
        'mako',
        'future',
        'pygments-doconce',
        'publish-doconce'
        ],
    #data_files=[(os.path.join("share", "man", "man1"),[man_filename,]),],
    package_data = {'': ['sphinx_themes.zip', 'html_images.zip', 'reveal.js.zip', 'deck.js.zip', 'csss.zip', 'latex_styles.zip']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Text Processing :: Markup :: XML',
    ]
)
