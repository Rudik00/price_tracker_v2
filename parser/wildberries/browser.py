async def _fetch_html_with_browser(
    browser, url: str, timeout: int = 60_000
) -> str:
    """Получение HTML-кода страницы с помощью Playwright (рендеринг JS)."""

    page = await browser.new_page()
    try:
        # Устанавливаем user-agent, чтобы выглядеть как обычный браузер.
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 "
            "Safari/537.36"
        })

        # Переходим на страницу 
        await page.goto(url, timeout=timeout)

        # Ждем 2 секунды
        await page.wait_for_timeout(2700)

        return await page.content()

    finally:
        await page.close()
