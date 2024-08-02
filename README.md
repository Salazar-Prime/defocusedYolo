# Defocused YOLO 

Create a bounding box around a bubble. USe the bounding box as a template for lacting similar objects in an video. 

## Getting Started

### Dependencies (requirements.txt)

* numpy
* pandas
* opencv-python-headless
* streamlit-drawable-canvas

#### Not in requirements.txt
* streamlit
  
### Installing

* Create a conda env
```
conda create -n <env-name> python=3.10
conda activate <env-name>
```
* Install Dependencies using pip
```
pip install streamlit
pip install -r requirements.txt 
```

### Executing program

* Clone the Repo
```
git clone https://github.com/Salazar-Prime/defocusedYolo
cd defocusedYolo
git checkout -b <branch-name> origin/<branch-name>
git fetch --all
```
* Start streamlit local server
```
streamlit run src/app.py
```
## TODO

- [x] Add bounding box canvas for finding the template in the video

## Authors

* [Varun Aggarwal](https://www.linkedin.com/in/aggarwal-v/)
* [Tri Vo](https://github.com/qtris123)

## Version History

* 0.2.0.0
    * User can draw BB for template matching
* 0.1.0.0
    * Initial Release

## License

This project is licensed under the [Creative Commons Legal Code](https://github.com/Salazar-Prime/defocusedYolo/blob/main/LICENSE) 

## Acknowledgments

Inspiration, code snippets, etc.
* [streamlit](streamlit.io)
* [streamlit-drawable-canvas](https://github.com/andfanilo/streamlit-drawable-canvas)
