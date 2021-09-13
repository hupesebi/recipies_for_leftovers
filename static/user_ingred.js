 // Add ingredient to inventory; stays on current page
 function ingredAddResult(result) {
    console.log(result);
    let ingredList = $("#ingred-list");
    let ingredientName = result.ingredient;
    if (ingredientName) {
      let ingredID = result.ingred_id;
      console.log(ingredID);
      ingredList[0].innerHTML = ingredList.html() + '<li class="row ingred-row"><span class="ingredient col-sm-8"> '+ingredientName.charAt(0).toUpperCase()+ingredientName.slice(1)+
      '</span><div class="del-button-td col-sm-2"><button class="delete-button btn btn-outline-secondary btn-sm ingred-del-buttons" name="ingredient" value="'+ingredID+'">&times;</button>'+
      '</div></li>';

      // $(".delete-button").on('click', delIngred);
      let alertDiv = document.createElement("div"); 
      $(alertDiv).addClass("alert alert-success alert-dismissible");
      $(alertDiv).attr("role", "alert");
      $(alertDiv).append('<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>Added to inventory: <strong>'+ ingredientName.charAt(0).toUpperCase()+ingredientName.slice(1)+'</strong>');
      $(alertDiv).appendTo("#alert-area");

    }
    else {
      let alertDiv = document.createElement("div"); 
      $(alertDiv).addClass("alert alert-warning alert-dismissible");
      $(alertDiv).attr("role", "alert");
      $(alertDiv).append('<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>Ingredient exists already.');
      $(alertDiv).appendTo("#alert-area");
    };
  }

  function addIngred(evt) {
    evt.preventDefault();

    let formInputs = {
      "ingredient": $("#ingredient").val()
    };

    $.post("/add_ingred", formInputs, ingredAddResult);

  }

  $("#add-ingred").on("submit", addIngred);


  // Delete ingredient from inventory; stays on current page
  function delIngred(evt) {
    evt.preventDefault();
    let formInputs = {
      "ingredient": this.value
    };

    let thisButton = this;
    let thisIngred = this.parentElement.previousElementSibling;
    console.log(thisIngred);
    // let thisTR = this.parentElement.parentElement.parentElement;
    let thisTR = this.parentElement.parentElement;

    $.post("/del_ingred", formInputs, function(){
      $(thisTR).remove();
      let alertDiv = document.createElement("div"); 
      $(alertDiv).addClass("alert alert-warning alert-dismissible");
      $(alertDiv).attr("role", "alert");
      $(alertDiv).append('<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>Removed from inventory: <strong>'+ thisIngred.innerText+'</strong>');
      $(alertDiv).appendTo("#alert-area");


    });;
  }

  $("#ingred-list").on('click', ".delete-button", delIngred);