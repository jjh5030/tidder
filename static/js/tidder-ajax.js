$(document).ready(function() {

	var story_id = $("div.upvote").attr("id");
	$('#' + story_id).upvote();

	// using jQuery
	function getCookie(name) {
	    var cookieValue = null;
	    if (document.cookie && document.cookie != '') {
	        var cookies = document.cookie.split(';');
	        for (var i = 0; i < cookies.length; i++) {
	            var cookie = jQuery.trim(cookies[i]);
	            // Does this cookie string begin with the name we want?
	            if (cookie.substring(0, name.length + 1) == (name + '=')) {
	                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                break;
	            }
	        }
	    }
	    return cookieValue;
	}
	var csrftoken = getCookie('csrftoken');

	$("#commenters").on("click", ".reply", function(event){
		event.preventDefault();
		//$("#postcomment").remove();
		var form = $("#postcomment").clone(true);
		form.find('.parent').val($(this).parent().parent().attr('id'));
		$(this).parent().append(form);
		//$("#reply-" + story_id).remove();
		this.style.display = 'none'
	});


});