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
    var thisButton = this;
    var instructions = $(thisButton)("ol.recipe-instructions");
  
    $(instructions).toggle();
  
    if ($(thisButton).text()=="View Instructions") {
      $(thisButton).text("Hide Instructions");
      instructions.css('display', 'block !important')
    }
    else {
      $(thisButton).text("View Instructions");
    }
  
    });
  
  
  
  