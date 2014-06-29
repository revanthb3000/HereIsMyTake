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