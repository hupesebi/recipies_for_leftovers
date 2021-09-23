//Remove recipe from user's recipe box
function deleteRecipe(evt) {
evt.preventDefault();

let thisButton = this;
let thisDiv = thisButton.parentElement.parentElement.parentElement;


let formInputs = {
    "recipe_id": this.value
};


$.post("/del_recipe", formInputs, function(){

    // alert("Recipe removed.");
    $(thisButton).html("&#10004");
    $(thisDiv).fadeOut();


});
}

$(".del-recipe").on('click', deleteRecipe);



//Display instructions on click 
$(".instructions-button").on("click", function(){
    let thisButton = this;
    let instructions = $(thisButton).siblings("ol.recipe-instructions");
    $(instructions).toggle();

    if ($(thisButton).text()=="View Instructions") {
    $(thisButton).text("Hide Instructions");
    }
    else {
      $(thisButton).text("View Instructions");
    }

    });

