$(document).ready(function () {

    $('#checkBoxAll').click(function () {
      if ($(this).is(":checked")) {
        $(".chkCheckBoxId").prop("checked", true)
      }else{
        $(".chkCheckBoxId").prop("checked", false)
      }
    });

    // bind this event to all delete buttons
    $(".delete").click(function(){

      // find the modal body
      var modal = $("#deleteArticleModal").find(".modal-body");       

      // loop through all the check boxes (class checkbox)
      $(".checkbox").each(function(index){

        // if they are checked, add them to the modal
        var articleId = $(this).val();

        if($(this).is(":checked")){

          // add a hidden input element to modal with article ID as value
          $(modal).append("<input name='articlesArray' value='"+articleId+"'  type='hidden' />")
        }
      });
    });

  });