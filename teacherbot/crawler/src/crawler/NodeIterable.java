package crawler;

import java.util.*;
import java.util.NoSuchElementException;

import org.jsoup.nodes.Node;

public class NodeIterable implements Iterable<Node> {

	private Node root;

	public NodeIterable(Node root) {
		this.root = root;
	}

	@Override
	public Iterator<Node> iterator() {
		return new NodeIterator(root);
	}
	
	private class NodeIterator implements Iterator<Node> {
		Deque<Node> stack;

		public NodeIterator(Node node) {
			stack  = new ArrayDeque<Node>();
			stack.push(node);
		}

		@Override
		public boolean hasNext() {
			return !stack.isEmpty();
		}

		@Override
		public Node next() {
			if (stack.isEmpty()) {
				throw new NoSuchElementException();
			} 
			Node node = stack.pop();
			List<Node> nodes  = new ArrayList<Node>(node.childNodes());
			Collections.reverse(nodes);
			for(Node child: nodes) {
				stack.push(child);
			}
			return node;
		}

		@Override 
		public void remove() {
			throw new UnsupportedOperationException();
		}


	}

}