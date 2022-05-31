# pyClipNSearchIt
Although a decade ago it was both feasible and normal to use standard relational databases for most types of data storage, the amount of generated data has since then grown exponentially, requiring new innovations to be made in the way of both indexing and processing methods. This to enable performing video identification at a sufficient enough scale. As such we have in this thesis developed pyClipNSearchIt, which is a highly performant video identification method especially tailored for big data applications. Using a combination of smart architectural design, as well as the cutting edge FENSHES technique for performing hemming distance comparisons inside full-text NoSQL engines, we display in our approach a significant improvement over earlier available video identification methods such as PYVIDID. Specifically, in measureable areas such as speed, size reduction and accuracy. The final result is as a highly scalable and cost efficient system, which can easily be used by professional and non-professional actors alike.

## Requirements
* Python 3.9+
* Elasticsearch cluster
    * Must have available ingest nodes

## Setup
* Run setup_frontend.py to install the frontend requirements and generate configuration file
    * Make sure to edit this file before running the next step
* Run setup_backend.py to set up the necessary elasticsearch indexes and pipelines

## Usage
Simply use the run.py script to run the program. Append the --help argument to see which arguments are valid.

## License
Copyright (C) 2022  Fredrik Wilhelm Thon Reite

This program is free software: you can redistribute it and/or modify
it under the terms of the [GNU General Public License v3.0](LICENSE) as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.