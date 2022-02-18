$(document).ready(function () {
    $("#checkbox1").click(function(){
      console.log($(this).val());
console.log(haha);
    },
    // bind this event to all delete buttons
    $(".delete").click(function(){

      // find the modal body
      var modal = $("#deleteArticleModal").find(".modal-body");       

      // loop through all the check boxes (class checkbox)
      $(".checkbox").each(function(index){

        // if they are checked, add them to the modal
        var userId = $(this).val();
        console.log(userId)
        if($(this).is(":checked")){

          // add a hidden input element to modal with article ID as value
          $(modal).append("<input name='userArray' value='"+userId+"'  type='hidden' />")
        }
      });
    })