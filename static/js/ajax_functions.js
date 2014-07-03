/**
 * This guy is used to change the follow status while viewing a user's profile dynamically. The follower count is also updated.
 * @param followURL
 */
function changeFollowStatus(followURL) {
	var xmlhttp;
	if (window.XMLHttpRequest) {
		// code for IE7+, Firefox, Chrome, Opera, Safari
		xmlhttp = new XMLHttpRequest();
	} else {
		// code for IE6, IE5
		xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
	}
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
			if(xmlhttp.responseText!="Invalid"){
				imageLink = document.getElementById("FollowActionImage").src;
				if(imageLink.indexOf("/follow.png") > -1){ //Check if it's a follow image present for now.
					document.getElementById("FollowActionImage").src = imageLink.replace("/follow.png","/unfollow.png");
				}
				else{
					document.getElementById("FollowActionImage").src = imageLink.replace("/unfollow.png","/follow.png");
				}
				document.getElementById("followerCount").innerHTML = xmlhttp.responseText;
			}
		}
	}
	xmlhttp.open("GET", followURL, true);
	xmlhttp.send();
}

/**
 * Thus function will be used to update the like status, like count and the image dynamically.
 */
function changeLikeStatus(likeLink, imageId, likeCountId){
	var xmlhttp;
	if (window.XMLHttpRequest) {
		// code for IE7+, Firefox, Chrome, Opera, Safari
		xmlhttp = new XMLHttpRequest();
	} else {
		// code for IE6, IE5
		xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
	}
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
			if(xmlhttp.responseText!="Invalid"){
				imageLink = document.getElementById(imageId).src;
				if(imageLink.indexOf("Positive.png") > -1){ //Check if it's a follow image present for now.
					document.getElementById(imageId).src = imageLink.replace("Positive.png","Negative.png");
				}
				else{
					document.getElementById(imageId).src = imageLink.replace("Negative.png","Positive.png");
				}
				document.getElementById(likeCountId).innerHTML = "(" + xmlhttp.responseText + ")";
			}
		}
	}
	xmlhttp.open("GET", likeLink, true);
	xmlhttp.send();
}