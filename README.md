# Defocused YOLO 

## Description

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
* Install dependencies using pip

### Executing program

* Clone the Repo
```
git clone https://github.com/Salazar-Prime/defocusedYolo --depth 1
cd defocusedYolo
pip install -r requirements.txt # optional if env is already setup 
pip install streamlit # optional if env is already setup 
```
* Start streamlit local server
```
streamlit run src/app.py
```

## Authors

* [Varun Aggarwal](https://www.linkedin.com/in/aggarwal-v/)

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the [Creative Commons Legal Code](https://github.com/Salazar-Prime/defocusedYolo/blob/main/LICENSE) 

## Acknowledgments

Inspiration, code snippets, etc.
* [streamlit](streamlit.io)
* [streamlit-drawable-canvas](https://github.com/andfanilo/streamlit-drawable-canvas)
