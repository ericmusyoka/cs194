package crawler;


import java.io.IOException;
import java.util.*;

import org.jsoup.nodes.Element;
import org.jsoup.nodes.Node;
import org.jsoup.nodes.TextNode;
import org.jsoup.select.Elements;
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;

public class WikipediaCrawler {
	private final String sourceUrl;

	private Queue<String> queue = new LinkedList<String>();

	private List<String> wikipediaData ;

	public WikipediaCrawler(String sourceUrl) {
		this.sourceUrl = sourceUrl;
		queue.offer(sourceUrl);
		wikipediaData = new ArrayList<String>();
	}

	//Adds a single page to the index
	public void crawl() throws IOException {
		String currentUrl = queue.poll();
		Elements paragraphs = getParagraphs(currentUrl);
		System.out.println(paragraphs.size());
		indexParagraphs(paragraphs);
		// addLinksInParagraphsToQueue(paragraphs);
	}

	//Reads wikipedia page and returns text within <p> tags
	public Elements getParagraphs(String url) throws IOException {
		Connection connection = Jsoup.connect(url);
		Document document = connection.get();
		return document.getElementById("mw-content-text").select("p");
	}

	public void processParagraph(Node paragraphNode) {
		for(Node node: new NodeIterable(paragraphNode)) {
			if (node instanceof TextNode) {
				wikipediaData.add(((TextNode) node).text());
			}
		}

	}

	public void indexParagraphs(Elements paragraphs) {
		for (Node node: paragraphs) {
			processParagraph(node);
		}
	}

	public List<String> getData() {
		return wikipediaData;
	}

	public static void main(String[] args) throws IOException {
		WikipediaCrawler wiki = new WikipediaCrawler("https://en.wikipedia.org/wiki/Egypt");
		wiki.crawl();
		System.out.println(wiki.getData().get(0));
	}

}