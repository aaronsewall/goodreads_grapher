"""
Graphs an goodreads author or series in matplotlib. Caches api calls use requests
cache.

Example URLs:
Author: https://www.goodreads.com/author/show/2565.Ian_Fleming"
Series: https://www.goodreads.com/series/49397-james-bond---extended-series
"""
import argparse
import itertools
import math
import re
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import requests_cache
from betterreads.book import GoodreadsBook
from betterreads.client import GoodreadsClient

requests_cache.install_cache("goodreads_cache")

DEFAULT_AUTHOR_BOOKS_PER_PAGE = 30
DEFAULT_SERIES_BOOKS_PER_PAGE = 100


def parse_args() -> argparse.Namespace:
    """
    Parses command line arguments.

    :returns None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--client-key",
        help="Goodreads client key, generate one at https://www.goodreads.com/api/keys",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--client-secret",
        help="Goodreads client secret, generate one at "
        "https://www.goodreads.com/api/keys",
        required=True,
    )
    parser.add_argument(
        "--cut-off",
        help="Define a cutoff for the graph, makes graphs more compact/legible",
        type=int,
        default=-1,
        required=False,
    )
    parser.add_argument(
        "--prompt-more-urls",
        help="Enable interactive url mode, which prompts for more URLs after generating"
        " a graph",
        action="store_true",
        required=False,
        default=False,
    )
    parser.add_argument(
        "--prompt-new-cutoff",
        help="Enable interactive cutoff mode, which prompts for a new cutoff number",
        action="store_true",
        required=False,
        default=False,
    )
    parser.add_argument(
        "--sort-by-rating",
        help="Sort the resulting graph by the rating descending",
        action="store_true",
        required=False,
        default=False,
    )
    parser.add_argument(
        "--min-num-ratings",
        help="The minimum number of ratings needed for a book to be in the graph. Only"
        "applies to authors mode",
        required=False,
        type=int,
        default=1,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--author", action="store_true", help="Flag to set author mode")
    group.add_argument("--series", action="store_true", help="Flag to set series mode")
    parser.add_argument(
        "urls",
        type=str,
        nargs="+",
        help="Enter as many goodreads urls as you like, must all be of the same type, "
        "authors or series",
    )
    return parser.parse_args()


def author_url_to_author_id(url: str) -> int:
    """
    Converts an author url into an author id.

    :param url: str
    :returns int, author id
    """
    raw_author_str = url.replace("https://www.goodreads.com/author/", "")
    author_rgx = r".*show\/(\d+)\..*"
    return int(re.search(author_rgx, raw_author_str).group(1))


def series_url_to_series_id(url: str) -> int:
    """
    Converts a series url into a series id.

    :param url: str
    :returns int, series id
    """
    raw_series_str = url.replace("https://www.goodreads.com/series/", "")
    series_rgx = r"(\d+)-.*"
    return int(re.search(series_rgx, raw_series_str).group(1))


def graph_series(
    gc: GoodreadsClient,
    url: str,
    cut_off: int,
    prompt_new_cutoff: bool,
    sort_by_rating: bool,
):
    """
    Generate a graph of an series' books where average rating is on the y axis and
    the x axis has each book on a scatter plot. Hover over a point to see the book's
    title.

    :param gc: GoodreadsClient
    :param url: str, url containing a series id
    :param cut_off: int, where to cut the graph off
    :param prompt_new_cutoff: bool, whether to prompt for a new cutoff
    :param sort_by_rating: bool, whether to sort the graph by rating descending
    """
    series_id = series_url_to_series_id(url)
    resp = gc.request("series/show", {"id": series_id, "page": 1})
    series_work = resp["series"]["series_works"]["series_work"]
    total = int(resp["series"]["series_works_count"])
    pages = math.ceil(int(total) / DEFAULT_SERIES_BOOKS_PER_PAGE) + 1
    if pages > 1:
        series_work.extend(
            list(
                itertools.chain(
                    *[
                        gc.request("series/show", {"id": series_id, "page": p})[
                            "series"
                        ]["series_works"]["series_work"]
                        for p in range(2, pages)
                    ]
                )
            )
        )
    series_books = [
        {
            **work["work"],
            **work["work"]["best_book"],
            "user_position": work["user_position"],
        }
        for work in series_work
    ]
    for i, book in enumerate(series_books):
        del series_books[i]["best_book"]
    series_df = pd.DataFrame(series_books)
    series_df.ratings_sum = series_df.ratings_sum.astype(int)
    series_df.ratings_count = series_df.ratings_count.astype(int)
    series_df.average_rating = series_df.ratings_sum / series_df.ratings_count
    while True:
        if sort_by_rating:
            graph_series_sort_by_average_rating(series_df, cut_off)
        else:
            graph_avg_rating_by_series_order(series_df, cut_off)
        if prompt_new_cutoff:
            NEW_CUT_OFF = int(input("New cut off number (Enter to cancel):") or 0)
            if NEW_CUT_OFF == 0:
                break
            else:
                cut_off = NEW_CUT_OFF
        else:
            break


def graph_avg_rating_by_series_order(series_df: pd.DataFrame, cut_off: int) -> None:
    """
    Graphs a series' books by average rating in the series order.

    :param series_df: DataFrame of a series' books
    :param cut_off: Where to cut the graph
    :returns None
    """
    avg_rating_in_series_order = series_df[["title", "average_rating"]][:cut_off]
    avg_rating_in_series_order.plot(
        kind="scatter", x="title", y="average_rating", xticks=[]
    )
    plt.show()


def graph_series_sort_by_average_rating(series_df: pd.DataFrame, cut_off: int) -> None:
    """
    Graphs a series' books sorted by average rating descending.

    :param series_df: DataFrame of a series' books
    :param cut_off: Where to cut the graph
    :returns None
    """
    book_by_average_rating = series_df[:cut_off].sort_values(
        ["average_rating"], ascending=False
    )[["title", "average_rating"]]
    book_by_average_rating.plot(
        kind="scatter", x="title", y="average_rating", xticks=[]
    )
    plt.show()


def author_books_total_pages(gc: GoodreadsClient, author_id: int) -> int:
    """
    Get the total of pages for an author's books, sorted by popularity on Goodreads.

    :param gc: GoodReadsClient
    :param author_id: int, id of an author
    :return: int, number of pages
    """
    resp = gc.request("author/list", {"id": author_id})
    total = int(resp["author"]["books"]["@total"])
    return math.ceil(int(total) / DEFAULT_AUTHOR_BOOKS_PER_PAGE) + 1


def author_books_for_page(
    gc: GoodreadsClient, author_id: int, page: int
) -> List[GoodreadsBook]:
    """
    Get the books for an author, sorted by popularity on Goodreads at a particular page.

    :param gc: GoodReadsClient
    :param author_id: int, id of an author
    :param page: int, page number to fetch
    :return List[GoodReadsBook]
    """
    return [
        GoodreadsBook({**book, "id": int(book["id"]["#text"])}, gc)
        for book in (
            gc.request("author/list", {"id": author_id, "page": page})["author"][
                "books"
            ]["book"]
        )
    ]


def author_books_all_pages(gc: GoodreadsClient, author_id: int) -> List[GoodreadsBook]:
    """
    Get all books for a particular author sorted by popularity on Goodreads.
    :param gc: GoodReadsClient
    :param author_id: int, id of an author
    :return List[GoodReadsBook]
    """
    return list(
        itertools.chain(
            *[
                author_books_for_page(gc, author_id, p)
                for p in list(range(1, author_books_total_pages(gc, author_id)))
            ]
        )
    )


def graph_author(
    gc: GoodreadsClient,
    url: str,
    cut_off: int,
    prompt_new_cutoff: bool = False,
    sort_by_rating: bool = False,
    min_num_ratings: int = 1,
) -> None:
    """
    Generate a graph of an author's books where average rating is on the y axis and
    the x axis has each book on a scatter plot. Hover over a point to see the book's
    title.

    :param gc: GoodreadsClient
    :param url: url that contains an author id
    :param cut_off: int defaults to nothing being cut off
    :param prompt_new_cutoff: bool default False
    :param sort_by_rating: bool default False
    :param min_num_ratings: int default 1
    :return None
    """
    author_id = author_url_to_author_id(url)
    author_books = author_books_all_pages(gc=gc, author_id=author_id)
    filtered_author_books = [
        book
        for book in author_books
        if int(author_id) in [atr.gid for atr in book.authors]
        and book.ratings_count > min_num_ratings
    ]
    author_books_df = pd.DataFrame([book._book_dict for book in filtered_author_books])
    author_books_df.average_rating = author_books_df.average_rating.astype(float)
    while True:
        if sort_by_rating:
            graph_author_sort_by_average_rating(author_books_df, cut_off)
        else:
            graph_avg_rating_by_popularity(author_books_df, cut_off)
        if prompt_new_cutoff:
            NEW_CUT_OFF = int(input("New cut off number (Enter to cancel): ") or 0)
            if NEW_CUT_OFF == 0:
                break
            else:
                cut_off = NEW_CUT_OFF
        else:
            break


def graph_average_rating_by_publication_date(
    author_books_df: pd.DataFrame, cut_off: int
) -> None:
    """
    Not used. Graphs average rating by publication date. Doesn't work well in practice,
    the default publication date is often for the reprinted version.

    TODO To make this effective, you would probably have to re-query the API per book
     to get a more reasonable "oldest" date for each book.

    :param author_books_df: DataFrame of an author's books
    :param cut_off: Where to cut the graph
    :returns None
    """
    # TODO calculate by the actual date but as a stand-in these fields are provided by
    #  the API.
    avg_rating_by_date = author_books_df[:cut_off].sort_values(
        ["publication_year", "publication_month", "publication_day"]
    )[["title_without_series", "average_rating"]]
    avg_rating_by_date.plot(
        kind="scatter", x="title_without_series", y="average_rating", xticks=[]
    )
    plt.show()


def graph_author_sort_by_average_rating(
    author_books_df: pd.DataFrame, cut_off: int
) -> None:
    """
    Graphs author's books sorted by average rating descending.
    :param author_books_df: DataFrame of an author's books
    :param cut_off: Where to cut the graph
    :returns None
    """
    book_by_average_rating = author_books_df[:cut_off].sort_values(
        ["average_rating"], ascending=False
    )[["title_without_series", "average_rating"]]
    book_by_average_rating.plot(
        kind="scatter", x="title_without_series", y="average_rating", xticks=[]
    )
    plt.show()


def graph_avg_rating_by_popularity(author_books_df: pd.DataFrame, cut_off: int) -> None:
    """
    Graphs average rating by popularity using the order that Goodreads provides.
    :param author_books_df: DataFrame of an author's books
    :param cut_off: Where to cut the graph
    :returns None
    """
    avg_rating_by_popularity = author_books_df[
        ["title_without_series", "average_rating"]
    ][:cut_off]
    avg_rating_by_popularity.plot(
        kind="scatter", x="title_without_series", y="average_rating", xticks=[]
    )
    plt.show()


def alternate_graph_avg_rating_by_popularity(
    author_books_df: pd.DataFrame, cut_off: int
) -> None:
    """
    Not used. Graphs average rating by popularity, and calculates popularity by ratings
    count instead of whatever order Goodreads uses.
    :param author_books_df: DataFrame of an author's books
    :param cut_off: Where to cut the graph
    :returns None
    """
    avg_rating_by_popularity = author_books_df.sort_values(
        "ratings_count", ascending=False
    )[["title_without_series", "average_rating"]][:cut_off]
    avg_rating_by_popularity.plot(
        kind="scatter", x="title_without_series", y="average_rating", xticks=[]
    )
    plt.show()


def main() -> None:
    args = parse_args()
    gc = GoodreadsClient(client_key=args.client_key, client_secret=args.client_secret)
    if args.series:
        for url in args.urls:
            graph_series(
                gc, url, args.cut_off, args.prompt_new_cutoff, args.sort_by_rating
            )
            if args.prompt_more_urls:
                while True:
                    raw_urls = input(
                        "Enter some more urls separated by spaces (Enter to cancel): "
                    )
                    if raw_urls != "":
                        urls = raw_urls.split(" ")
                        for url in urls:
                            graph_series(
                                gc,
                                url,
                                args.cut_off,
                                args.prompt_new_cutoff,
                                args.sort_by_rating,
                            )
                    else:
                        break

    if args.author:
        for url in args.urls:
            graph_author(
                gc,
                url,
                args.cut_off,
                args.prompt_new_cutoff,
                args.sort_by_rating,
                args.min_num_ratings,
            )
        if args.prompt_more_urls:
            while True:
                raw_urls = input(
                    "Enter some more urls separated by spaces (Enter to cancel): "
                )
                if raw_urls != "":
                    urls = raw_urls.split(" ")
                    for url in urls:
                        graph_author(
                            gc,
                            url,
                            args.cut_off,
                            args.prompt_new_cutoff,
                            args.sort_by_rating,
                            args.min_num_ratings,
                        )
                else:
                    break


if __name__ == "__main__":
    main()
