String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g,"");
}

String.prototype.ltrim = function() {
    return this.replace(/^\s+/,"");
}

String.prototype.rtrim = function() {
    return this.replace(/\s+$/,"");
}

function myform () {

	$('form.myform').find('li label').not('.nocmx').each(function (i) {
		var labelContent = this.innerHTML;
		var labelWidth = document.defaultView.getComputedStyle (this, '').getPropertyValue ('width');
		var labelSpan = document.createElement ('span');
		labelSpan.style.display = 'block';
		labelSpan.style.width = labelWidth;
		labelSpan.innerHTML = labelContent;
		this.style.display = '-moz-inline-box';
		this.innerHTML = null;
		this.appendChild(labelSpan);
	});
}

function turn_post_fields_gray() {

	if($("#heater_title").val() === "title goes here") {
		$("#heater_title").css('color', '#CCC');
	}

	if($("#heater_slug").val() === "slug-goes-here") {
		$("#heater_slug").css('color', '#CCC');
	}

	if($("#heater_body").text() === "content goes here") {
		$("#heater_body").css('color', '#CCC');
	}

	if($("#heater_tags").val() === "tags, go, here") {
		$("#heater_tags").css('color', '#CCC');
	}
}

function handle_on_focus_post_fields() {

	$("#heater_title").focus(function() {
		if($("#heater_title").val() === "title goes here") {
			$("#heater_title").val('');
			$("#heater_title").css('color', 'black');
		}

	});

	$("#heater_slug").focus(function() {
		if($("#heater_slug").val() === "slug-goes-here") {
			$("#heater_slug").val('');
			$("#heater_slug").css('color', 'black');
		}

	});

	$("#heater_body").focus(function() {
		if($("#heater_body").text() === "content goes here") {
			$("#heater_body").text('');
			$("#heater_body").css('color', 'black');
		}

	});

	$("#heater_tags").focus(function() {
		if($("#heater_tags").val() === "tags, go, here") {
			$("#heater_tags").val('');
			$("#heater_tags").css('color', 'black');
		}

	});
}

$(document).ready(function(){
	myform();
	turn_post_fields_gray();
	handle_on_focus_post_fields();
});
