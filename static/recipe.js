  $(".card-columns").on('click', ".add-recipe", function(evt) {
      evt.preventDefault();
      let thisButton = this;
      let thisDiv = thisButton.parentElement.parentElement.parentElement;
    
      let formInputs = {
        "recipe_id": this.value
      };
    
      $.post("/add_recipe", formInputs, function(){
        $(thisButton).html("&#10004; Saved!");
        $(thisDiv).fadeOut();
      });
    });
  
  $(".recipe-instructions").hide()
  
  //Display instructions on click 
  $(".card-columns").on('click', ".instructions-button", function(){
    let thisButton = this;
    let instructions = $(thisButton).siblings("ol.recipe-instructions");
    
  
    $(instructions).toggle();
  
    if ($(thisButton).text()=="View Instructions") {
      instructions.show()
      $(thisButton).text("Hide Instructions");
    }
    else {
      $(thisButton).text("View Instructions");
      instructions.hide()
    }
  
    });
  
  
  
  