function show_fields(transition){
	if(typeof transition === "undefined")
		transition = true;
	
	var autogen = django.jQuery('#id_autogenerate_text').is(':checked');
	var type = django.jQuery('#id_type').val();
	
	var field_body = django.jQuery('div.field-body_template');
	var field_body_html = django.jQuery('div.field-body_template_html');
	var field_autogen = django.jQuery('div.field-autogenerate_text');
	
	if(type == 'text/plain'){
		//in plain text mode, hide html fields and show text body
		if(transition){
			field_body.slideDown();
			field_body_html.slideUp();
			field_autogen.slideUp();
		}else{
			field_body.show();
			field_body_html.hide();
			field_autogen.hide();
		}
	}else if(autogen){
		//in html with autogen mode, show html fields and hide text body
		if(transition){
			field_body.slideUp();
			field_body_html.slideDown();
			field_autogen.slideDown();
		}else{
			field_body.hide();
			field_body_html.show();
			field_autogen.show();
		}
	}else{
		//in html without autogen mode, show all fields
		if(transition){
			field_body.slideDown();
			field_body_html.slideDown();
			field_autogen.slideDown();
		}else{
			field_body.show();
			field_body_html.show();
			field_autogen.show();
		}
	}
}

django.jQuery(function(){
	show_fields(false);
	django.jQuery('#id_type, #id_autogenerate_text').change(show_fields);
});