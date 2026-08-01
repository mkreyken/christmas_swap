# Create a Random List of givers (chain) that considers all passed givers and interpersonal relationship


* data is in (data/base.json)
* Is of the form


      {
      "families" : {
            "fam1head" : [ "fam1head" ],
            "fam2head" : [ "fam2head", "fam2mem1", "fam2mem2"],
      },
      "otherCostsBi" : {
      },
      "kids" : [ "comment1"],
      "ignore" : [ "NoLonger1", "NoLonger2"]
    _}


* Year files (data/ 2026.json) is a give -> receiver list complete cycle

      {
          "#": "comment",
          "Name1": "Name2",
          "Name2": "Name3",
          "Name3": "Name1"
       }