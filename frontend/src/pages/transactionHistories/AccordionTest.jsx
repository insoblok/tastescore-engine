import { useRef } from 'react';
import { useAccordion, useAccordionItem, useAccordionItemContext } from '@react-aria/accordion';
import { useAccordionState } from '@react-stately/accordion';
import { mergeProps } from '@react-aria/utils';

function Accordion(props) {
  const state = useAccordionState(props);
  const ref = useRef();
  const { accordionProps } = useAccordion(props, state, ref);

  return (
    <div {...accordionProps} ref={ref} className="w-full max-w-md mx-auto">
      {[...state.collection].map((item) => (
        <AccordionItem key={item.key} item={item} state={state} />
      ))}
    </div>
  );
}

function AccordionItem({ item, state }) {
  const ref = useRef();
  const { buttonProps, regionProps } = useAccordionItem({ key: item.key }, state, ref);
  const context = useAccordionItemContext();

  return (
    <div className="mb-2 border border-gray-200 rounded-md overflow-hidden">
      <h3>
        <button
          {...buttonProps}
          ref={ref}
          className="w-full p-4 text-left bg-gray-50 hover:bg-gray-100 transition-colors duration-200 flex justify-between items-center"
        >
          <span className="font-medium">{item.props.title}</span>
          <span 
            className={`transform transition-transform duration-200 ${state.expandedKeys.has(item.key) ? 'rotate-180' : ''}`}
            aria-hidden="true"
          >
            ▼
          </span>
        </button>
      </h3>
      <div
        {...regionProps}
        className={`px-4 overflow-hidden ${state.expandedKeys.has(item.key) ? 'block' : 'hidden'}`}
      >
        <div className="pb-4 pt-2">{item.props.children}</div>
      </div>
    </div>
  );
}

// Usage example
export default function AccordionTest() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Accessible FAQ Accordion</h1>
      <Accordion>
        <AccordionItem key="1" title="What is React Aria?">
          React Aria is a library of React Hooks that provides accessible UI primitives
          for your design system.
        </AccordionItem>
        <AccordionItem key="2" title="Why use an accessible accordion?">
          Accessible accordions ensure all users, including those using screen readers
          or keyboard navigation, can interact with your content.
        </AccordionItem>
        <AccordionItem key="3" title="How does keyboard navigation work?">
          Users can tab to each accordion header and use Space or Enter to toggle content.
          Arrow keys can also be used to navigate between items.
        </AccordionItem>
      </Accordion>
    </div>
  );
}
