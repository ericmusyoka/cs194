package crawler;


import java.io.IOException;
import java.util.*;

import org.jsoup.nodes.Node;
import org.jsoup.nodes.TextNode;
import org.jsoup.select.Elements;
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;

import java.io.BufferedWriter;
import java.io.FileWriter;

public class WikipediaCrawler {
	private final String sourceUrl;
	
	private int docCount;

	private Queue<String> queue = new LinkedList<String>();

	private List<String> wikipediaData ;
	private Set<String> history;

	public WikipediaCrawler(String sourceUrl, int docCount) {
		this.sourceUrl = sourceUrl;
		this.docCount = docCount + 1;
		queue.offer(sourceUrl);
		wikipediaData = new ArrayList<String>();
		history = new HashSet<String>();
	}

	//Adds a single page to the index
	public void crawl() {
		while(!queue.isEmpty()) {
			String currentUrl = queue.poll();
			history.add(currentUrl);
			try {
				Elements paragraphs = getParagraphs(currentUrl);
				indexParagraphs(paragraphs);
				addLinksInParagraphsToQueue(paragraphs);
				saveDocument();
				docCount++;
				wikipediaData.clear();
			} catch(IOException ex) {
				//do nothing
			}
	
		}
	}
	
	public void saveDocument() {
		String document = "";
		for(String paragraph: wikipediaData) {
			document += paragraph;
		}
		
		FileWriter fileWriter = null;
		BufferedWriter bufferedWriter = null;

		try {
			fileWriter = new FileWriter("data/" + docCount + ".txt");
			bufferedWriter = new BufferedWriter(fileWriter);
			bufferedWriter.write(document);
		} catch(IOException ex) {
			ex.printStackTrace();
		} finally {
			try {
				if (bufferedWriter != null) {
					bufferedWriter.close();
				}
				if (fileWriter != null) {
					fileWriter.close();
				}
				
			} catch(IOException ex) {
				ex.printStackTrace();
			}
		}
		
	}
	
	
	public void addLinksInParagraphsToQueue(Elements paragraphs) {
		for(Element paragraph: paragraphs) {
			NodeIterable paragraphIterable = new NodeIterable(paragraph);
			for(Node node: paragraphIterable) {
				if(node instanceof Element) {
					Element nodeElement = (Element)node;
					if(nodeElement.tagName().equals("a")) {
						String url = node.attr("href");
						String absUrl = "https://www.wikipedia.org" + url;
						if(isWikipediaLink(url) && shouldQueue(absUrl)) {
							queue.add(absUrl);
							System.out.println(absUrl);
						}
					}
				}
			}
			
		}
	}
	
	private boolean isWikipediaLink(String link) {
		return link.startsWith("/wiki/");
	}
	
	private boolean shouldQueue(String url) {
		return !queue.contains(url);
	}

	//Reads wikipedia page and returns text within <p> tags
	public Elements getParagraphs(String url) throws IOException {
		Connection connection = Jsoup.connect(url);
		Document document = connection.get();
		return document.getElementById("mw-content-text").select("p");
	}

	public void processParagraph(Node paragraphNode) {
		String text = "";
		for(Node node: new NodeIterable(paragraphNode)) {
			if (node instanceof TextNode) {
				text += ((TextNode) node).text();
			}
		}
		wikipediaData.add(text);
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
		WikipediaCrawler wiki = new WikipediaCrawler("https://en.wikipedia.org/wiki/Portal:History", 0);
		wiki.crawl();
//		List<String> data = wiki.getData();
//		for(int i=0; i<data.size(); i++) {
//			System.out.println(wiki.getData().get(i));	
//		}
	}

}