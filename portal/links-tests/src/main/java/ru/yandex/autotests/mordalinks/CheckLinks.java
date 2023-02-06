package ru.yandex.autotests.mordalinks;

import org.apache.log4j.Logger;
import ru.yandex.autotests.mordalinks.beans.MordaLink;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import static ru.yandex.autotests.mordalinks.utils.MordaLinkUtils.getAllLinks;

/**
 * Update stable exports data
 *
 * @goal check-links
 */
public class CheckLinks {

    private static final Logger LOG = Logger.getLogger(CheckLinks.class);
    private static final ExecutorService executorService = Executors.newFixedThreadPool(30);

    public void execute() throws InterruptedException {
        List<MordaLink> linksWithErrors = new ArrayList<MordaLink>();
        List<MordaLink> allLinks = getAllLinks();
        LOG.info("Found " + allLinks.size() + " links in Elliptics");
        for (MordaLink link : allLinks) {
            executorService.submit(new CheckLinkTask(link, linksWithErrors));
        }
        executorService.shutdown();
        if (!executorService.awaitTermination(20, TimeUnit.MINUTES)) {
            executorService.shutdownNow();
        }
        System.out.println("Links with errors:\n" + linksWithErrors);
    }

    public static void main(String[] args) throws InterruptedException {
        new CheckLinks().execute();
    }

}
