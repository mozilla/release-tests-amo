# -*- coding: utf-8 -*-
import time

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from pages.desktop.home import Home
from pages.desktop.search import Search


@pytest.mark.nondestructive
def test_search_loads_and_navigates_to_correct_page(base_url, selenium):
    page = Home(selenium, base_url).open()
    addon_name = page.featured_extensions.list[0].name
    search = page.search.search_for(addon_name)
    search_name = search.result_list.extensions[0].name
    assert addon_name in search_name
    assert search_name in search.result_list.extensions[0].name


@pytest.mark.nondestructive
def test_search_loads_correct_results(base_url, selenium):
    page = Home(selenium, base_url).open()
    addon_name = page.featured_extensions.list[0].name
    items = page.search.search_for(addon_name)
    assert addon_name in items.result_list.extensions[0].name


@pytest.mark.skip
@pytest.mark.nondestructive
def test_legacy_extensions_do_not_load(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'Video Download Manager'
    items = page.search.search_for(term)
    for item in items.result_list.extensions:
        assert term not in item.name


@pytest.mark.parametrize('category, sort_attr', [
    ['Top Rated', 'rating'],
    ['Trending', 'hotness']])
def test_filter_sort_by(base_url, selenium, category, sort_attr):
    """Test searching for an addon and sorting."""
    Home(selenium, base_url).open()
    addon_name = 'fox'
    selenium.get('{}/search/?&q={}&sort={}'.format(
        base_url, addon_name, sort_attr)
    )
    search_page = Search(selenium, base_url)
    results = search_page.result_list.extensions
    if sort_attr == 'rating':
        for result in search_page.result_list.extensions:
            assert result.rating > 4
    else:
        assert len(results) == 25


@pytest.mark.nondestructive
def test_filter_by_users(base_url, selenium):
    Home(selenium, base_url).open()
    addon_name = 'fox'
    sort = 'users'
    selenium.get('{}/search/?&q={}&sort={}'.format(
        base_url, addon_name, sort)
    )
    search_page = Search(selenium, base_url)
    results = [getattr(result, sort)
               for result in search_page.result_list.extensions]
    assert sorted(results, reverse=True) == results


# This test will be moved to a different suite since here the test is inconclusive
@pytest.mark.skip
@pytest.mark.nondestructive
def test_incompative_extensions_show_as_incompatible(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'Incompatible platform'
    results = page.search.search_for(term)
    time.sleep(2)
    for item in results.result_list.extensions:
        if term == item.name:
            detail_page = item.click()
            assert detail_page.is_compatible is False
            # assert detail_page.button_state is False


@pytest.mark.nondestructive
def test_search_suggestion_term_is_higher(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'Flagfox'
    suggestions = page.search.search_for(term, execute=False)
    assert suggestions[0].name == term


@pytest.mark.nondestructive
def test_special_chars_dont_break_suggestions(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'Flagfox'
    special_chars_term = f'{term}%ç√®å'
    suggestions = page.search.search_for(special_chars_term, execute=False)
    results = [item.name for item in suggestions]
    assert term in results


@pytest.mark.nondestructive
def test_uppercase_has_same_suggestions(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'fox'
    first_suggestions_list = page.search.search_for(term, execute=False)
    first_results = [item.name for item in first_suggestions_list]
    page.search.clear_search_field()
    second_suggestions_list = page.search.search_for(term.upper(), execute=False)
    # Sleep to let autocomplete update.
    time.sleep(1)
    second_results = [item.name for item in second_suggestions_list]
    assert first_results == second_results


@pytest.mark.nondestructive
def test_esc_key_closes_suggestion_list(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'Flagfox'
    page.search.search_for(term, execute=False)
    action = ActionChains(selenium)
    # Send ESC key to browser
    action.send_keys(Keys.ESCAPE).perform()
    with pytest.raises(NoSuchElementException):
        selenium.find_element_by_css_selector(
            'AutoSearchInput-suggestions-list')


@pytest.mark.xfail
@pytest.mark.nondestructive
def test_long_terms_dont_break_suggestions(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'videodo'
    suggestions = page.search.search_for(term, execute=False)
    # Sleep to let autocomplete update.
    # time.sleep(2)
    term_max_len = 33
    suggestion_names = [item.name for item in suggestions]
    # print(suggestion_names)
    for suggestion_name in suggestion_names:
        assert len(suggestion_name) <= term_max_len


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_blank_search_loads_results_page(base_url, selenium):
    page = Home(selenium, base_url).open()
    search_page = page.search.search_for('', execute=True)
    results = search_page.result_list.extensions
    assert len(results) == 25
    for result in results:
        assert result.has_recommended_badge
    sort = 'users'
    results = [getattr(result, sort)
               for result in search_page.result_list.extensions]
    assert sorted(results, reverse=True) == results
    search_page.next_page()
    assert '2' in search_page.page_number


@pytest.mark.nondestructive
def test_suggestions_change_by_query(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'pass'
    suggestions = page.search.search_for(term, execute=False)
    first_suggestions_list = [item.name for item in suggestions]
    new_term = 'word'
    suggestions = page.search.search_for(new_term, execute=False)
    # allows for search suggestions to update
    time.sleep(2)
    second_suggestions_list = [item.name for item in suggestions]
    assert first_suggestions_list != second_suggestions_list


@pytest.mark.nondestructive
def test_select_result_with_enter_key(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'Flagfox'
    page.search.search_for(term, execute=False)
    action = ActionChains(selenium)
    action.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    # give time to the detail page to load
    page.wait_for_title_update(term)


@pytest.mark.nondestructive
def test_select_result_with_click(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'Flagfox'
    suggestions = page.search.search_for(term, execute=False)
    result = suggestions[0].root
    action = ActionChains(selenium)
    action.move_to_element(result).click().perform()
    # give time to the detail page to load
    page.wait_for_title_update(term)


@pytest.mark.nondestructive
def test_suggestion_icon_is_displayed(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'Flagfox'
    suggestions = page.search.search_for(term, execute=False)
    suggestions[0].addon_icon()


@pytest.mark.nondestructive
def test_recommended_badge_is_displayed(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'Flagfox'
    suggestions = page.search.search_for(term, execute=False)
    suggestions[0].recommended_badge()


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_filter_default(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'Flagfox'
    page.search.search_for(term)
    search_page = Search(selenium, base_url)
    """Validates the default sort filters present on search results page"""
    search_page.default_sort_filter()


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_filter_recommended(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 's'
    results = page.search.search_for(term)
    search_page = Search(selenium, base_url)
    search_page.recommended_filter()
    for result in results.result_list.extensions:
        assert result.has_recommended_badge


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_filter_extensions(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'fox'
    page.search.search_for(term)
    search_page = Search(selenium, base_url)
    search_page.filter_by_type("Extension")
    search_page.wait_for_contextcard_update("extensions")
    assert len(search_page.result_list.themes) == 0


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_filter_themes(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'fox'
    page.search.search_for(term)
    search_page = Search(selenium, base_url)
    search_page.filter_by_type("Theme")
    search_page.wait_for_contextcard_update("themes")
    assert len(search_page.result_list.themes) == 25


@pytest.mark.desktop_only
@pytest.mark.nondestructive
def test_selected_result_is_highlighted(base_url, selenium):
    page = Home(selenium, base_url).open()
    term = 'Flagfox'
    suggestions = page.search.search_for(term, execute=False)
    result = suggestions[0].root
    action = ActionChains(selenium)
    action.move_to_element(result).click_and_hold().perform()
    assert page.search.highlighted_suggestion
