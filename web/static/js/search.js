function search_method() {
    keyword = document.search_form.q.value;
    document.search_form.action = "/";
    document.search_form.submit();
}
